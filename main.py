import flet as ft #import flet libs
import json
import requests
from datetime import datetime
from controllers import gettoken, getproducts, get_tables, reserve_table, occupy_table, release_table, get_categories  # Atualizando importação
import subprocess
import sys
import os
import time
import signal
import atexit

# Add at the top of your file, before the main function
server_process = None

def start_server():
    global server_process
    try:
        # Get the directory where main.py is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_path = os.path.join(current_dir, 'simple_server.py')
        
        # Start the server as a subprocess
        server_process = subprocess.Popen([sys.executable, server_path], 
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        
        # Wait a bit for the server to start
        time.sleep(2)
        
        # Check if server started successfully
        if server_process.poll() is None:
            print("Server started successfully")
        else:
            stdout, stderr = server_process.communicate()
            print(f"Server failed to start: {stderr.decode()}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        sys.exit(1)

def stop_server():
    global server_process
    if server_process:
        print("Stopping server...")
        if sys.platform == 'win32':
            server_process.terminate()
        else:
            os.kill(server_process.pid, signal.SIGTERM)
        server_process.wait()
        print("Server stopped")

# Register the cleanup function
atexit.register(stop_server)

body = ft.Container(
        col=8.5,
        content=ft.Column(controls=[])
    )
def getproducts():
    return json.loads(requests.get("http://127.0.0.1:8000/").text)
def main(page:ft.Page):
    page.title="EasyPOS"
    page.padding=0
    page.window.min_width=1200
    global body
    

    # Define ALL global containers first
    sidebar = ft.Container(
        bgcolor=ft.Colors.WHITE,
        col=1,
        border_radius=10,
        content=ft.Column(controls=[])
    )

   

    side_right = ft.Container(
        padding=10,
        bgcolor=ft.Colors.WHITE,
        col=2.5,
        border_radius=10,
        content=ft.Column(controls=[])
    )

    main_container = ft.Container(
        padding=8,
        expand=True,
        bgcolor=ft.Colors.INDIGO_100,
        content=ft.ResponsiveRow([sidebar, body, side_right])
    )

    # Define other global variables
    cart_items = []  # Lista para controlar itens no carrinho
    products = []
    listView = ft.ListView(expand=True)
    
    # Criar textos para total e quantidade de itens
    items_text = ft.Text("items: 0 quanty: 0", color=ft.Colors.GREY_500)
    total_text = ft.Text("$0.00", size=30, weight="bold", color=ft.Colors.ORANGE)

    def update_total():
        total = sum(item["quantity"] * item["price"] for item in cart_items)
        total_text.value = f"${total:.2f}"
        items_text.value = f"items: {len(cart_items)} quanty: {sum(item['quantity'] for item in cart_items)}"
        page.update()

    def update_item_quantity(e, item_index, delta):
        if 0 < cart_items[item_index]["quantity"] + delta:
            cart_items[item_index]["quantity"] += delta
            quantity_text = listView.controls[item_index].controls[1].controls[0].controls[1].content.controls[0]
            quantity_text.value = str(cart_items[item_index]["quantity"])
            update_total()
            page.update()

    def remove_item(e, index):
        cart_items.pop(index)
        listView.controls.pop(index)
        update_total()
        page.update()

    def addtoCart(e):
        product = e.control.data
        # Verifica se o produto já está no carrinho
        existing_item = next(
            (item for item in cart_items if item["id"] == product["id"]), 
            None
        )
        
        if existing_item:
            # Se já existe, apenas aumenta a quantidade
            item_index = cart_items.index(existing_item)
            update_item_quantity(None, item_index, 1)
        else:
            # Se não existe, adiciona novo item
            cart_item = {
                "id": product["id"],
                "name": product["name"],
                "price": float(product["price"]),
                "image": product["image"],
                "quantity": 1
            }
            cart_items.append(cart_item)
            
            listView.controls.append(
                ft.Column([
                    ft.Row([
                        ft.Image(product["image"], width=50, height=50),
                        ft.Row([
                            ft.Column([
                                ft.Text(product["name"], weight="bold"),
                                ft.Text(f"price: ${product['price']}", color=ft.Colors.ORANGE)
                            ]),
                            ft.Container(
                                content=ft.Text(
                                    f"${float(product['price']):.2f}",
                                    color=ft.Colors.ORANGE,
                                    size=20,
                                    weight="bold"
                                ),
                                padding=10
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, expand=1)
                    ]),
                    ft.Row([
                        ft.Row([
                            ft.IconButton(
                                icon=ft.icons.REMOVE,
                                on_click=lambda e, i=len(cart_items)-1: update_item_quantity(e, i, -1)
                            ),
                            ft.Container(
                                border_radius=3,
                                width=40,
                                height=25,
                                bgcolor=ft.Colors.INDIGO_50,
                                content=ft.Row([
                                    ft.Text("1")
                                ], alignment=ft.MainAxisAlignment.CENTER)
                            ),
                            ft.IconButton(
                                icon=ft.icons.ADD,
                                on_click=lambda e, i=len(cart_items)-1: update_item_quantity(e, i, 1)
                            )
                        ]),
                        ft.IconButton(
                            ft.icons.DELETE,
                            on_click=lambda e, i=len(cart_items)-1: remove_item(e, i)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ])
            )
            update_total()

    def try_login(e):
        username = username_field.value
        password = password_field.value
        
        if not username or not password:
            snack = ft.SnackBar(
                content=ft.Text("Por favor, preencha todos os campos."),
                action="OK",
                bgcolor=ft.Colors.RED_400,
            )
            page.overlay.clear()
            page.overlay.append(snack)
            snack.open = True
            page.update()
            return

        # Ativar loading no botão
        login_button.content = ft.Row(
            [ft.ProgressRing(width=16, height=16), ft.Text("Entrando...", size=16)],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        login_button.disabled = True
        page.update()

        try:
            response = gettoken(username, password)
            
            if "access" in response:
                # Guardar dados da sessão
                page.client_storage.set("access_token", response["access"])
                page.client_storage.set("refresh_token", response["refresh"])
                page.client_storage.set("user_id", response["id"])
                page.client_storage.set("username", response["user"])
                
                # Login bem sucedido
                snack = ft.SnackBar(
                    content=ft.Text("Login realizado com sucesso!"),
                    action="OK",
                    bgcolor=ft.Colors.GREEN_400,
                )
                page.overlay.clear()
                page.overlay.append(snack)
                snack.open = True
                page.update()
                initialize_app()
                page.go("/home")
            else:
                # Login falhou
                error_message = response.get("detail", "Usuário ou senha inválidos")
                snack = ft.SnackBar(
                    content=ft.Text(error_message),
                    action="OK",
                    bgcolor=ft.Colors.RED_400,
                )
                page.overlay.clear()
                page.overlay.append(snack)
                snack.open = True
                page.update()
        except Exception as e:
            # Erro de conexão ou outro erro
            snack = ft.SnackBar(
                content=ft.Text(f"Erro ao conectar ao servidor: {str(e)}"),
                action="OK",
                bgcolor=ft.Colors.RED_400,
            )
            page.overlay.clear()
            page.overlay.append(snack)
            snack.open = True
            page.update()
        finally:
            # Restaurar botão ao estado original
            login_button.content = ft.Text("Entrar", size=16, weight="bold")
            login_button.disabled = False
            page.update()

    # Definindo os campos de login DEPOIS da função try_login
    username_field = ft.TextField(
        label="Usuário",
        border_color=ft.Colors.GREY_400,
        height=50,
    )
    password_field = ft.TextField(
        label="Senha",
        password=True,
        can_reveal_password=True,
        border_color=ft.Colors.GREY_400,
        height=50,
    )

    login_button = ft.FilledButton(
        content=ft.Text(
            "Entrar",
            size=16,
            weight="bold"
        ),
        width=320,
        height=50,
        bgcolor=ft.Colors.ORANGE_500,
        on_click=try_login
    )

    def initialize_app():
        global body
        # Show loading in a centered container with larger size
        loading_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.ProgressRing(width=50, height=50),
                    ft.Text("Carregando...", size=16, weight="bold")
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            alignment=ft.alignment.center,
            expand=True,
            bgcolor=ft.Colors.RED

        )
        
        body.content = loading_container
        page.update()

        try:
            # Get token and categories
            token = page.client_storage.get("access_token")
            categories_response = get_categories()
            categories = categories_response.get("detail", [])

            # Create category buttons
            category_buttons = [
                ft.TextButton(
                    category['cg_name'], 
                    on_click=lambda e: print(f"Selected category: {category['cg_name']}")
                )
                for category in categories
            ]

            # Load products with loading state
            products.clear()  # Clear existing products
            try:
                product_data = getproducts()
                for product in product_data:
                    products.append(
                        ft.Container(
                            alignment=ft.alignment.center,
                            bgcolor=ft.Colors.WHITE,
                            border_radius=10,
                            content=ft.Column([
                                ft.Container(
                                    content=ft.Image(
                                        product['image'],
                                        width=page.window.width/3,
                                        fit=ft.ImageFit.COVER
                                    ),
                                    expand=1
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[
                                        ft.Container(
                                            content=ft.Column([
                                                ft.Text(product['name'], weight="bold", size=15),
                                                ft.Text(
                                                    f"Price: ${product['price']:.2f}",
                                                    weight="bold",
                                                    color=ft.Colors.ORANGE
                                                ),
                                                ft.FilledButton(
                                                    "add",
                                                    bgcolor=ft.Colors.ORANGE_600,
                                                    width=100,
                                                    on_click=addtoCart,
                                                    data=product  # Mudando de key para data
                                                )
                                            ], height=100)
                                        ),
                                    ]
                                )
                            ])
                        )
                    )
            except Exception as e:
                # Show error if products fail to load
                products.append(
                    ft.Container(
                        content=ft.Text(f"Error loading products: {str(e)}"),
                        alignment=ft.alignment.center
                    )
                )

            # Initialize views with loading states
            def show_tables_view():
                # Show loading state
                loading_container = ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.ProgressRing(width=50, height=50),
                            ft.Text("Carregando mesas...", size=16, weight="bold")
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20
                    ),
                    alignment=ft.alignment.center,
                    expand=True
                )
                
                body.content = loading_container
                page.update()

                try:
                    # Fetch tables data
                    tables_response = get_tables()
                    tables = tables_response.get("detail", [])  # Get tables from response

                    tables_view = ft.Row(
                        wrap=True,
                        spacing=20,
                        controls=[]
                    )

                    def filter_tables(e):
                        search = e.control.value.lower() if e and e.control else ""
                        filtered = [
                            table for table in tables
                            if (search in str(table.get("tb_number", "")).lower() or
                                search in str(table.get("tb_guest_name", "")).lower() or
                                search in str(table.get("tb_status", "")).lower())
                        ]
                        
                        tables_view.controls = [
                            ft.Container(
                                width=250,
                                height=150,
                                border_radius=20,
                                bgcolor=ft.Colors.GREY_50,
                                padding=15,
                                content=ft.Column([
                                    ft.Row([
                                        ft.Text(f"T{table.get('tb_number', '')}", 
                                              size=20, 
                                              weight="bold"),
                                        ft.Text(table.get('tb_time', ''), 
                                              color=ft.Colors.GREY_700),
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                    ft.Container(height=10),
                                    ft.Text(table.get('tb_guest_name', ''), size=16),
                                    ft.Text(
                                        table.get('tb_status', ''),
                                        size=14,
                                        color={
                                            'Available': ft.Colors.GREEN,
                                            'Occupied': ft.Colors.BLUE,
                                            'Reserved': ft.Colors.ORANGE
                                        }.get(table.get('tb_status', ''), ft.Colors.GREY)
                                    ),
                                    ft.Text(
                                        f"{table.get('tb_guests', '')} Guests", 
                                        color=ft.Colors.GREY_700
                                    )
                                ]),
                                border=ft.border.all(
                                    width=2,
                                    color={
                                        'Available': ft.Colors.GREEN,
                                        'Occupied': ft.Colors.BLUE,
                                        'Reserved': ft.Colors.ORANGE
                                    }.get(table.get('tb_status', ''), ft.Colors.GREY)
                                )
                            ) for table in filtered
                        ]
                        page.update()

                    search_field = ft.TextField(
                        hint_text="Search guest",
                        prefix_icon=ft.Icons.SEARCH,
                        filled=True,
                        bgcolor=ft.Colors.GREY_50,
                        on_change=filter_tables,
                        width=300
                    )

                    # Initialize view with all tables
                    filter_tables(None)

                    body.content = ft.Column([
                        ft.Container(
                            bgcolor=ft.Colors.WHITE,
                            padding=20,
                            border_radius=10,
                            content=ft.Column([
                                ft.Row([
                                    ft.Text("Tables", size=40, weight="bold"),
                                    search_field
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Container(height=20),
                                tables_view
                            ])
                        )
                    ])

                except Exception as e:
                    body.content = ft.Column([
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.icons.ERROR_OUTLINE, 
                                       color=ft.colors.RED, 
                                       size=40),
                                ft.Text(f"Error loading tables: {str(e)}",
                                       text_align=ft.TextAlign.CENTER),
                                ft.FilledButton(
                                    "Try again",
                                    on_click=lambda _: show_tables_view()
                                )
                            ]),
                            alignment=ft.alignment.center
                        )
                    ])
                    print(f"Tables error: {e}")
                
                page.update()

            def show_orders_view():
                # Show centered loading while fetching orders
                loading_container = ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.ProgressRing(width=50, height=50),
                            ft.Text("Carregando pedidos...", size=16, weight="bold")
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20
                    ),
                    alignment=ft.alignment.center,
                    expand=True
                )
                
                body.content = loading_container
                page.update()

                try:
                    # Fetch orders data
                    # ... rest of orders view code ...
                    body.content = ft.Column([
                        ft.Container(
                            bgcolor=ft.Colors.WHITE,
                            padding=20,
                            border_radius=10,
                            content=ft.Column([
                                ft.Row([
                                    ft.Text("Orders", size=30, weight="bold"),
                                    ft.Container(
                                        width=300,
                                        content=ft.TextField(
                                            hint_text="Search menu...",
                                            prefix_icon=ft.Icons.SEARCH,
                                            filled=True,
                                            bgcolor=ft.Colors.GREY_50,
                                        )
                                    )
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Row([
                                    ft.TextButton("All"),
                                    ft.TextButton("last Month"),
                                ]),
                                ft.DataTable(
                                    bgcolor=ft.Colors.WHITE,
                                    border_radius=10,
                                    heading_row_height=50,
                                    heading_text_style=ft.TextStyle(
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.BLACK,
                                    ),
                                    columns=[
                                        ft.DataColumn(ft.Text("Transaction ID")),
                                        ft.DataColumn(ft.Text("Date")),
                                        ft.DataColumn(ft.Text("Amount")),
                                        ft.DataColumn(ft.Text("Orders")),
                                        ft.DataColumn(ft.Text("Category")),
                                        ft.DataColumn(ft.Text("Menu")),
                                    ],
                                    rows=[
                                        ft.DataRow(cells=[
                                            ft.DataCell(ft.Text("12415346512")),
                                            ft.DataCell(ft.Text("Wed 1:00pm")),
                                            ft.DataCell(ft.Text("$18.99")),
                                            ft.DataCell(ft.Text("2")),
                                            ft.DataCell(
                                                ft.Container(
                                                    content=ft.Text("Food", color=ft.Colors.BLUE),
                                                    bgcolor=ft.Colors.BLUE_50,
                                                    padding=5,
                                                    border_radius=15,
                                                )
                                            ),
                                            ft.DataCell(ft.Text("Mac and Cheese")),
                                        ]),
                                        ft.DataRow(cells=[
                                            ft.DataCell(ft.Text("12415346512")),
                                            ft.DataCell(ft.Text("Wed 7:20am")),
                                            ft.DataCell(ft.Text("$4.50")),
                                            ft.DataCell(ft.Text("3")),
                                            ft.DataCell(
                                                ft.Container(
                                                    content=ft.Text("Food", color=ft.Colors.BLUE),
                                                    bgcolor=ft.Colors.BLUE_50,
                                                    padding=5,
                                                    border_radius=15,
                                                )
                                            ),
                                            ft.DataCell(ft.Text("Chili Cheese Dog")),
                                        ]),
                                        # ... mais linhas de pedidos ...
                                    ],
                                ),
                                ft.Container(
                                    content=ft.Text("Load More", color=ft.Colors.ORANGE),
                                    on_click=lambda _: print("Load more clicked"),
                                    alignment=ft.alignment.center,
                                )
                            ])
                        )
                    ])
                except Exception as e:
                    body.content = ft.Column([
                        ft.Container(
                            content=ft.Text(f"Error loading orders: {str(e)}"),
                            alignment=ft.alignment.center
                        )
                    ])
                page.update()

            # Initialize home view with loading state
            def show_home_view():
                # Show centered loading while fetching home data
                loading_container = ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.ProgressRing(width=50, height=50),
                            ft.Text("Carregando produtos...", size=16, weight="bold")
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20
                    ),
                    alignment=ft.alignment.center,
                    expand=True
                )
                
                body.content = loading_container
                page.update()

                try:
                    body.content = ft.Column(
                        controls=[
                            ft.Container(
                                bgcolor=ft.Colors.WHITE,
                                height=55,
                                border_radius=10,
                                padding=10,
                                content=ft.Row(
                                    category_buttons, 
                                    alignment=ft.MainAxisAlignment.SPACE_AROUND
                                )
                            ),
                            ft.GridView(
                                controls=products,
                                expand=1,
                                runs_count=5,
                                max_extent=200,
                                child_aspect_ratio=0.8,
                                spacing=5,
                                run_spacing=5
                            )
                        ]
                    )
                except Exception as e:
                    body.content = ft.Column([
                        ft.Container(
                            content=ft.Text(f"Error loading home view: {str(e)}"),
                            alignment=ft.alignment.center
                        )
                    ])
                    
                page.update()

            # Initialize rest of the app
            # Appbar
            page.appbar = ft.AppBar(
                leading=ft.Container(
                    content=ft.Row([
                        ft.Text('Easy', weight="bold", size=25),
                        ft.Text('POS', weight="bold", color=ft.Colors.ORANGE_500, size=25)
                    ]),
                    padding=ft.Padding(left=14, top=0, right=0, bottom=0)
                ),
                actions=[
                    ft.Container(
                        padding=ft.Padding(left=0, top=0, right=14, bottom=0),
                        content=ft.Row([
                            ft.TextButton('Home', on_click=lambda _: show_home_view()),
                            ft.TextButton('Mesas', on_click=lambda _: show_tables_view()),
                            ft.TextButton('Pedidos', on_click=lambda _: show_orders_view()),
                            ft.TextButton('Clientes', on_click=lambda _: show_customers_view()),
                            ft.TextButton('Caixa', on_click=lambda _: show_cashier_view()),
                            ft.FilledButton('Novo Pedido', bgcolor=ft.Colors.ORANGE),
                    ft.IconButton(icon=ft.Icons.NOTIFICATIONS)
                        ], spacing=8)
                    ),
                    ft.PopupMenuButton(
                        items=[
                            ft.PopupMenuItem("Conta"),
                            ft.PopupMenuItem("Configurações", on_click=lambda _: show_settings_view()),
                            ft.PopupMenuItem("Ajuda"),
                            ft.PopupMenuItem("Sobre"),
                        ]
                    )
                ]
            )
            #end of appbar

            def navigation_change(e):
                selected_index = e.control.selected_index
                if selected_index == 0:
                    show_home_view()
                elif selected_index == 1:
                    show_tables_view()
                elif selected_index == 2:
                    show_orders_view()
                elif selected_index == 3:
                    show_customers_view()
                elif selected_index == 4:
                    show_cashier_view()

            sidebar = ft.Container(
                bgcolor=ft.Colors.WHITE,
                col=1,
                border_radius=10,
                content=ft.Column(
            controls=[
                        ft.Container(
                            expand=1,
                            content=ft.NavigationRail(
                                selected_index=0,
                                on_change=navigation_change,
                destinations=[
                                    ft.NavigationRailDestination(
                                        icon=ft.Icons.COFFEE,
                                        label="Coffee",
                                        selected_icon=ft.Icons.COFFEE,
                                    ),
                                    ft.NavigationRailDestination(
                                        icon=ft.Icons.TABLE_BAR,
                                        label="Mesas",
                                        selected_icon=ft.Icons.TABLE_BAR,
                                    ),
                                    ft.NavigationRailDestination(
                                        icon=ft.Icons.FOOD_BANK,
                                        label="Pedidos",
                                        selected_icon=ft.Icons.FOOD_BANK,
                                    ),
                                    ft.NavigationRailDestination(
                                        icon=ft.Icons.PEOPLE,
                                        label="Clientes",
                                        selected_icon=ft.Icons.PEOPLE,
                                    ),
                                    ft.NavigationRailDestination(
                                        icon=ft.Icons.POINT_OF_SALE,
                                        label="Caixa",
                                        selected_icon=ft.Icons.POINT_OF_SALE,
                                    ),
                                ],
                                expand=1,
                                bgcolor=ft.Colors.WHITE
                            )
                        ),
                        ft.Container(
                            expand=1,
                            content=ft.Column(
                                expand=1,
                                controls=[
                                    ft.NavigationRail(
                                        height=80,
                                        on_change=lambda e: show_settings_view(),
                                        destinations=[
                                            ft.NavigationRailDestination(
                                                icon=ft.Icons.SETTINGS,
                                                label="Configurações",
                                            )
                                        ],
                                        bgcolor=ft.Colors.WHITE
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.END
                            )
                        ),
                    ],
                )
            )
            body = ft.Container(
                col=8.5,
                content=ft.Column(controls=[])
            )

        #side right
            side_right = ft.Container(
                padding=10,
                bgcolor=ft.Colors.WHITE,
                col=2.5,
                border_radius=10,
                content=ft.Column(
            controls=[
                ft.Container(height=200,content=ft.Column([
                    ft.Text("Invoice no: 3764749874",color=ft.Colors.GREY_500),
                    ft.Divider(height=1),
                    ft.Row([
                        ft.Icon(ft.Icons.RESTAURANT,size=40,color=ft.Colors.ORANGE),
                        ft.Column([
                            ft.Text("Easy POS",weight="bold",size=25),
                            ft.Text("easypos@gmail.com",color=ft.Colors.GREY_400)
                        ])

                    ]),
                    ft.Row([
                        ft.Text("table 04",weight="bold",color=ft.Colors.ORANGE),
                        ft.Text("Order #536733",weight="bold")
                    ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=1),
                ])),
                listView,#hire list container
                ft.Container(padding=10,content=ft.Column([
                    ft.Divider(height=1),
                    ft.Row([
                        ft.Column([
                            ft.Text("Total",weight="bold"),
                            items_text
                        ]),
                        total_text
                    ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ])),
                ft.CupertinoButton("Print Invoice",bgcolor=ft.Colors.INDIGO_50,color=ft.Colors.GREY_800,width=300),
                ft.CupertinoButton("Payments",bgcolor=ft.Colors.GREEN_600,width=300)
            ]
                )
            )
            
            # Update main_container content instead of creating new one
            main_container.content.controls = [sidebar, body, side_right]

            # Dados estáticos para demonstração
            tables_data = [
                {"number": "01", "status": "Ocupada", "orders": 2, "total": "$45.00"},
                {"number": "02", "status": "Livre", "orders": 0, "total": "$0.00"},
                {"number": "03", "status": "Reservada", "orders": 0, "total": "$0.00"},
                {"number": "04", "status": "Ocupada", "orders": 1, "total": "$32.50"},
            ]

            def show_cashier_view():
                body.content = ft.Column([
                    ft.Container(
                        bgcolor=ft.Colors.WHITE,
                        padding=20,
                        border_radius=10,
                        content=ft.Column([
                            ft.Text("Caixa", size=30, weight="bold"),
                            ft.Row([
                                ft.Container(
                                    expand=1,
                                    content=ft.Column([
                                        ft.Text("Resumo do Dia", weight="bold", size=20),
                                        ft.DataTable(
                                            columns=[
                                                ft.DataColumn(ft.Text("Descrição")),
                                                ft.DataColumn(ft.Text("Valor"), numeric=True),
                                            ],
                                            rows=[
                                                ft.DataRow(cells=[
                                                    ft.DataCell(ft.Text("Total Vendas")),
                                                    ft.DataCell(ft.Text("R$ 1.250,00")),
                                                ]),
                                                ft.DataRow(cells=[
                                                    ft.DataCell(ft.Text("Dinheiro")),
                                                    ft.DataCell(ft.Text("R$ 450,00")),
                                                ]),
                                                ft.DataRow(cells=[
                                                    ft.DataCell(ft.Text("Cartão")),
                                                    ft.DataCell(ft.Text("R$ 800,00")),
                                                ]),
                                            ],
                                        )
                                    ])
                                ),
                                ft.VerticalDivider(),
                                ft.Container(
                                    expand=1,
                                    content=ft.Column([
                                        ft.Text("Operações", weight="bold", size=20),
                                        ft.FilledButton(
                                            "Abrir Caixa",
                                            bgcolor=ft.Colors.GREEN,
                                            width=200
                                        ),
                                        ft.FilledButton(
                                            "Fechar Caixa",
                                            bgcolor=ft.Colors.RED,
                                            width=200
                                        ),
                                        ft.FilledButton(
                                            "Sangria",
                                            bgcolor=ft.Colors.ORANGE,
                                            width=200
                                        ),
                                    ])
                                )
                            ])
                        ])
                    )
                ])
                page.update()

            def show_settings_view():
                body.content = ft.Column([
                    ft.Container(
                        bgcolor=ft.Colors.WHITE,
                        padding=20,
                        border_radius=10,
                        content=ft.Column([
                            ft.Text("Configurações", size=30, weight="bold"),
                            ft.Tabs(
                                selected_index=0,
                                tabs=[
                                    ft.Tab(
                                        text="Geral",
                                        content=ft.Container(
                                            padding=20,
                                            content=ft.Column([
                                                ft.TextField(label="Nome da Empresa"),
                                                ft.TextField(label="CNPJ"),
                                                ft.TextField(label="Endereço"),
                                                ft.TextField(label="Telefone"),
                                                ft.TextField(label="Email"),
                                                ft.FilledButton("Salvar", bgcolor=ft.Colors.BLUE)
                                            ])
                                        )
                                    ),
                                    ft.Tab(
                                        text="Impressora",
                                        content=ft.Container(
                                            padding=20,
                                            content=ft.Column([
                                                ft.Dropdown(
                                                    label="Selecione a Impressora",
                                                    options=[
                                                        ft.dropdown.Option("Impressora 1"),
                                                        ft.dropdown.Option("Impressora 2"),
                                                    ]
                                                ),
                                                ft.FilledButton("Testar Impressão", bgcolor=ft.Colors.BLUE)
                                            ])
                                        )
                                    ),
                                ]
                            )
                        ])
                    )
                ])
                page.update()

            # Definindo as diferentes views
            def show_customers_view():
                body.content = ft.Column([
                    ft.Container(
                        bgcolor=ft.Colors.WHITE,
                        padding=20,
                        border_radius=10,
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Customers", size=30, weight="bold"),
                                ft.Container(
                                    width=300,
                                    content=ft.TextField(
                                        hint_text="Search customers...",
                                        prefix_icon=ft.Icons.SEARCH,
                                        filled=True,
                                        bgcolor=ft.Colors.GREY_50,
                                    )
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.DataTable(
                                bgcolor=ft.Colors.WHITE,
                                border_radius=10,
                                heading_row_height=50,
                                heading_text_style=ft.TextStyle(
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLACK,
                                ),
                                columns=[
                                    ft.DataColumn(ft.Text("Customer")),
                                    ft.DataColumn(ft.Text("Email")),
                                    ft.DataColumn(ft.Text("Total Orders")),
                                    ft.DataColumn(ft.Text("Status")),
                                    ft.DataColumn(ft.Text("Actions")),
                                ],
                                rows=[
                                    ft.DataRow(cells=[
                                        ft.DataCell(
                                            ft.Row([
                                                ft.CircleAvatar(
                                                    content=ft.Text("JS"),
                                                    bgcolor=ft.Colors.BLUE_100,
                                                ),
                                                ft.Text("João Silva")
                                            ])
                                        ),
                                        ft.DataCell(ft.Text("joao@email.com")),
                                        ft.DataCell(ft.Text("5")),
                                        ft.DataCell(
                                            ft.Container(
                                                content=ft.Text("Active", color=ft.Colors.GREEN),
                                                bgcolor=ft.Colors.GREEN_50,
                                                padding=5,
                                                border_radius=15,
                                            )
                                        ),
                                        ft.DataCell(
                                            ft.Row([
                                                ft.IconButton(icon=ft.Icons.EDIT),
                                                ft.IconButton(icon=ft.Icons.DELETE),
                                            ])
                                        ),
                                    ]),
                                    # ... mais linhas de clientes ...
                                ],
                            ),
                        ])
                    )
                ])
                page.update()

            # Inicialize com a view home
            show_home_view()
            page.add(main_container)

        except Exception as e:
            # Show error if initialization fails
            body.content = ft.Column([
                ft.Container(
                    content=ft.Text(f"Error initializing app: {str(e)}"),
                    alignment=ft.alignment.center
                )
            ])
            page.update()

    def check_auth():
        
        # Verificar se já existe uma sessão válida
        access_token = page.client_storage.get("access_token")
        if (access_token):
            # Se já estiver logado, vai direto para home
            initialize_app()
            page.go("/home")
            return True
        return False

    def route_change(route):
        page.views.clear()
        
        if page.route == "/login":
            if check_auth():
                return
            
            # Usando os campos já definidos
            page.views.append(
                ft.View(
                    "/login",
                    [
                        ft.Container(
                            expand=True,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Column(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    ft.Text('Easy', size=45, weight="bold"),
                                                    ft.Text('POS', size=45, weight="bold", color=ft.Colors.ORANGE)
                                                ],
                                            ),
                                            ft.Container(height=50),
                                            ft.Container(
                                                width=400,
                                                bgcolor=ft.Colors.WHITE,
                                                border_radius=8,
                                                padding=ft.padding.all(30),
                                                shadow=ft.BoxShadow(
                                                    spread_radius=1,
                                                    blur_radius=15,
                                                    color=ft.Colors.BLACK12,
                                                ),
                                                content=ft.Column(
                                                    spacing=20,
                                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                    controls=[
                                                        username_field,
                                                        password_field,
                                                        ft.Container(height=10),
                                                        login_button,
                                                    ],
                                                ),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            bgcolor=ft.Colors.GREY_50,
                        )
                    ],
                    bgcolor=ft.Colors.GREY_50,
                    padding=0
                )
            )
        elif page.route == "/home":
            # Verificar se está autenticado
            if not page.client_storage.get("access_token"):
                page.go("/login")
                return
                
            page.views.append(
                ft.View(
                    "/home",
                    [main_container],
                    padding=0
                )
            )
        
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Iniciar verificando autenticação
    if not check_auth():
        page.go("/login")

ft.app(target=main)