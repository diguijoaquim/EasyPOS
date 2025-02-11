from fastapi import WebSocket
from typing import Dict, Set, List, Optional
from pydantic import BaseModel
from enum import Enum

class MessageType(Enum):
    PERSONAL = "personal"  # Message for a single user
    DIRECT = "direct"      # Message between two users
    GROUP = "group"        # Message for a group
    BROADCAST = "broadcast"  # Message for everyone

class Message(BaseModel):
    """
    Pydantic model for message validation
    """
    message_type: MessageType
    content: str
    sender_id: str
    recipient_id: Optional[str] = None  # For personal or direct messages
    group_id: Optional[str] = None      # For group messages

class Group(BaseModel):
    """
    Pydantic model for group information
    """
    group_id: str
    name: str
    members: Set[str]

class ConnectionManager:
    def __init__(self):
        # Store active connections: {user_id: set(websocket)}
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Store group information: {group_id: Group}
        self.groups: Dict[str, Group] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """
        Connect a new user's websocket
        - Accepts the connection
        - Creates a new set for the user if they don't exist
        - Adds the websocket to user's set of connections
        """
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    async def disconnect(self, websocket: WebSocket, user_id: str):
        """
        Disconnect a user's websocket
        - Removes the websocket from user's connections
        - Cleans up empty user entries
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    def create_group(self, group_id: str, name: str, members: Set[str]) -> Group:
        """
        Create a new group with specified members
        Returns the created group
        """
        group = Group(group_id=group_id, name=name, members=members)
        self.groups[group_id] = group
        return group

    def add_to_group(self, group_id: str, user_id: str) -> bool:
        """
        Add a user to an existing group
        Returns True if successful, False if group doesn't exist
        """
        if group_id in self.groups:
            self.groups[group_id].members.add(user_id)
            return True
        return False

    def remove_from_group(self, group_id: str, user_id: str) -> bool:
        """
        Remove a user from a group
        Returns True if successful, False if group doesn't exist
        """
        if group_id in self.groups:
            self.groups[group_id].members.remove(user_id)
            return True
        return False

    async def send_personal_message(self, message: str, user_id: str):
        """
        Send a message to a single user through all their active connections
        Useful for system messages or notifications
        """
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_text(message)

    async def send_direct_message(self, message: str, sender_id: str, recipient_id: str):
        """
        Send a direct message between two users
        Message is sent to both sender and recipient
        """
        # Send to recipient
        if recipient_id in self.active_connections:
            for connection in self.active_connections[recipient_id]:
                await connection.send_text(f"From {sender_id}: {message}")
        
        # Send confirmation to sender
        if sender_id in self.active_connections:
            for connection in self.active_connections[sender_id]:
                await connection.send_text(f"To {recipient_id}: {message}")

    async def send_group_message(self, message: str, group_id: str, sender_id: str):
        """
        Send a message to all members of a specific group
        Sender is identified in the message
        """
        if group_id in self.groups:
            group = self.groups[group_id]
            for member_id in group.members:
                if member_id in self.active_connections:
                    for connection in self.active_connections[member_id]:
                        await connection.send_text(
                            f"Group {group.name} - From {sender_id}: {message}"
                        )

    async def broadcast(self, message: str, sender_id: str, exclude_user: str = None):
        """
        Broadcast a message to all connected users
        - Optional exclude_user parameter to skip specific user
        - Sender is identified in the message
        """
        for user_id, connections in self.active_connections.items():
            if user_id != exclude_user:
                for connection in connections:
                    await connection.send_text(f"Broadcast from {sender_id}: {message}")

# Example FastAPI implementation
"""
from fastapi import FastAPI

app = FastAPI()
manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            message = Message(**data)
            
            if message.message_type == MessageType.PERSONAL:
                await manager.send_personal_message(
                    message.content, 
                    message.recipient_id
                )
            
            elif message.message_type == MessageType.DIRECT:
                await manager.send_direct_message(
                    message.content,
                    message.sender_id,
                    message.recipient_id
                )
            
            elif message.message_type == MessageType.GROUP:
                await manager.send_group_message(
                    message.content,
                    message.group_id,
                    message.sender_id
                )
            
            elif message.message_type == MessageType.BROADCAST:
                await manager.broadcast(
                    message.content,
                    message.sender_id
                )
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await manager.disconnect(websocket, user_id)

# Example group creation
@app.post("/create_group")
async def create_group(group_id: str, name: str, members: List[str]):
    return manager.create_group(group_id, name, set(members))
"""