import json
import requests
from datetime import datetime, timedelta

def gettoken(username, password):
    url = 'https://ayt.sal.gy/api/v1/login/'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFTOKEN': 'ij9D6844EG1CnPwtynRx7RPRCKJp47T2CBgHTkbbJCTmqQ1RqGCeXWCkM2o84XMK'
    }
    data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def getproducts():
    return json.loads(requests.get("http://127.0.0.1:8000/").text)

def get_tables():
    """Retorna o estado atual das mesas"""
    tables = {
        "tables": [
            {
                "number": "T14",
                "status": "Available",
                "capacity": 4,
                "section": "Main",
            },
            {
                "number": "T13",
                "status": "Filled",
                "capacity": 2,
                "section": "Window",
                "occupied_by": "João Silva",
                "occupied_since": "2024-01-29T14:30:00",
                "expected_available": "2024-01-29T16:30:00",
                "order_id": "ORD-001"
            },
            {
                "number": "T17",
                "status": "Reserved",
                "capacity": 6,
                "section": "VIP",
                "reserved_by": "Maria Santos",
                "reserved_for": "2024-01-29T19:00:00",
                "reservation_id": "RES-001"
            },
            {
                "number": "T24",
                "status": "Available Soon",
                "capacity": 4,
                "section": "Terrace",
                "occupied_by": "Carlos Lima",
                "occupied_since": "2024-01-29T12:00:00",
                "expected_available": "2024-01-29T14:00:00",
                "order_id": "ORD-002"
            }
        ],
        "statistics": {
            "total_tables": 20,
            "available": 8,
            "filled": 6,
            "reserved": 4,
            "available_soon": 2
        }
    }
    return tables

def update_table_status(table_number, new_status, details=None):
    """
    Atualiza o status de uma mesa
    details pode incluir: occupied_by, reserved_by, expected_available, etc.
    """
    table_info = {
        "number": table_number,
        "status": new_status,
        "updated_at": datetime.now().isoformat()
    }
    
    if details:
        table_info.update(details)
    
    return {
        "success": True,
        "table": table_info
    }

def reserve_table(table_number, customer_name, reservation_time):
    """Faz uma reserva para uma mesa"""
    details = {
        "reserved_by": customer_name,
        "reserved_for": reservation_time,
        "reservation_id": f"RES-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    }
    return update_table_status(table_number, "Reserved", details)

def occupy_table(table_number, customer_name, duration_hours=2):
    """Ocupa uma mesa"""
    now = datetime.now()
    details = {
        "occupied_by": customer_name,
        "occupied_since": now.isoformat(),
        "expected_available": (now + timedelta(hours=duration_hours)).isoformat(),
        "order_id": f"ORD-{now.strftime('%Y%m%d%H%M%S')}"
    }
    return update_table_status(table_number, "Filled", details)

def release_table(table_number):
    """Libera uma mesa"""
    return update_table_status(table_number, "Available")

def add_order(order_details):
    # Simula a adição de um pedido
    print(f"Adding order: {order_details}")
    return {"status": "success", "order_id": 12345}

def add_table(table_details):
    # Simula a adição de uma mesa
    print(f"Adding table: {table_details}")
    return {"status": "success", "table_id": 67890}

def add_product(product_details):
    # Simula a adição de um produto
    print(f"Adding product: {product_details}")
    return {"status": "success", "product_id": 54321}

def get_customers():
    try:
        return requests.get('http://127.0.0.1:8000/customers').text
    except:
        return []

def get_orders():
    try:
        return requests.get('http://127.0.0.1:8000/orders').text
    except:
        return []
    


def get_categories(token):
    url = "https://ayt.sal.gy/api/v1/cat/lst"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch categories: {response.status_code}", "details": response.text}
    