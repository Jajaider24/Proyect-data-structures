import flet as ft

def PanelConcurrency(page):
    page.title = "Panel Simulación de Concurrencia"
    textField_width = 220
    textField_height = 50
    async def open_menu(e):
        await page.push_route("/")

    # Contenedor Izquierdo (70%) y Derecho (30%)
    return ft.View(
        route="/concurrencypanel",
        padding=0, # Elimina bordes externos de la ventana
        controls=[
            ft.Row(
                expand=True, # Permite que los contenedores usen expand=7 y expand=3
                spacing=0,
                controls=[
                    # PANEL IZQUIERDO (70%)
                    ft.Container(
                        content=ft.Text("Contenido Principal", color=ft.Colors.WHITE, size=30),
                        bgcolor=ft.Colors.BLUE_GREY_800, 
                        expand=7, 
                        alignment=ft.Alignment.CENTER,
                    ),
                    
                    # PANEL DERECHO (30%)
                    ft.Container(
                        expand=3,
                        padding=20,
                        alignment=ft.Alignment.CENTER,
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment.BOTTOM_CENTER,
                            end=ft.Alignment.TOP_CENTER,
                            colors=[
                                ft.Colors.GREY,
                                ft.Colors.LIGHT_BLUE,
                            ],
                        ),
                        content=ft.Column(
                            spacing=20,
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            scroll = ft.ScrollMode.ALWAYS,
                            expand = True,
                            controls=[
                                ft.Text("Ingrese los Datos del Vuelo", size = 20, weight=ft.FontWeight.BOLD),
                                ft.TextField(label="Código del Vuelo", 
                                            label_style = ft.TextStyle(color = ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
                                            cursor_color = ft.Colors.BLACK, 
                                            text_style= ft.TextStyle(color=ft.Colors.BLACK_87, weight=ft.FontWeight.BOLD),
                                            border_color = ft.Colors.BLACK, 
                                            width=textField_width, 
                                            height=textField_height, 
                                            hint_text="Ingrese el código", 
                                            hint_style=ft.TextStyle(color=ft.Colors.BLACK)),
                                ft.TextField(label="Ciudad de Origen", 
                                            label_style = ft.TextStyle(color = ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
                                            cursor_color = ft.Colors.BLACK, 
                                            text_style= ft.TextStyle(color=ft.Colors.BLACK_87, weight=ft.FontWeight.BOLD), 
                                            border_color = ft.Colors.BLACK,
                                            width=textField_width, 
                                            height=textField_height,
                                            hint_text="Ingrese el Origen",
                                            hint_style=ft.TextStyle(color=ft.Colors.BLACK)),
                                ft.TextField(label="Ciudad de Destino",
                                            label_style = ft.TextStyle(color = ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
                                            cursor_color = ft.Colors.BLACK, 
                                            text_style= ft.TextStyle(color=ft.Colors.BLACK_87, weight=ft.FontWeight.BOLD),
                                            border_color = ft.Colors.BLACK,
                                            width=textField_width, 
                                            height=textField_height, 
                                            hint_text="Ingrese el Destino",
                                            hint_style=ft.TextStyle(color=ft.Colors.BLACK)),
                                ft.TextField(label="Hora de Salida", 
                                            label_style = ft.TextStyle(color = ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
                                            cursor_color = ft.Colors.BLACK, 
                                            text_style= ft.TextStyle(color=ft.Colors.BLACK_87, weight=ft.FontWeight.BOLD), 
                                            border_color = ft.Colors.BLACK,
                                            width=textField_width, 
                                            height=textField_height, 
                                            hint_text="Ingrese Hora de Salida",
                                            hint_style=ft.TextStyle(color=ft.Colors.BLACK)),
                                ft.TextField(label="Precio del Vuelo", 
                                            label_style = ft.TextStyle(color = ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
                                            cursor_color = ft.Colors.BLACK, 
                                            text_style= ft.TextStyle(color=ft.Colors.BLACK_87, weight=ft.FontWeight.BOLD), 
                                            border_color = ft.Colors.BLACK,
                                            width=textField_width, 
                                            height=textField_height, 
                                            hint_text="Ingrese el precio",
                                            hint_style=ft.TextStyle(color=ft.Colors.BLACK)),
                                ft.TextField(label="Número de Pasajeros", 
                                            label_style = ft.TextStyle(color = ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
                                            cursor_color = ft.Colors.BLACK, 
                                            text_style= ft.TextStyle(color=ft.Colors.BLACK_87, weight=ft.FontWeight.BOLD), 
                                            border_color = ft.Colors.BLACK,
                                            width=textField_width, 
                                            height=textField_height, 
                                            hint_text="Número de Pasajeros",
                                            hint_style=ft.TextStyle(color=ft.Colors.BLACK)),
                                ft.TextField(label="Prioridad",  
                                            label_style = ft.TextStyle(color = ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
                                            cursor_color = ft.Colors.BLACK, 
                                            text_style= ft.TextStyle(color=ft.Colors.BLACK_87, weight=ft.FontWeight.BOLD), 
                                            border_color = ft.Colors.BLACK,
                                            width=textField_width, 
                                            height=textField_height, 
                                            hint_text="Ingrese la Prioridad",
                                            hint_style=ft.TextStyle(color=ft.Colors.BLACK)),
                                ft.Container(
                                    content=ft.Switch(label="Promoción", value=False, label_text_style=ft.TextStyle(color = ft.Colors.BLACK, size = 15)),
                                    width=textField_width, # Mismo ancho que tus TextFields
                                    alignment=ft.Alignment.CENTER_LEFT, # Alinea el switch a la izquierda del contenedor
                                ),
                                ft.Container(
                                    content=ft.Switch(label="   Alerta", value=False, label_text_style=ft.TextStyle(color = ft.Colors.BLACK, size = 15)),
                                    width=textField_width,
                                    alignment=ft.Alignment.CENTER_LEFT,
                                ),
                                ft.Button("Agregar a Cola", style=ft.ButtonStyle(padding = 10,
                                                            shape = ft.RoundedRectangleBorder(radius = 10),
                                                            text_style=ft.TextStyle(size=15))),
                                ft.Button("Procesar", width = 150, height=50, style=ft.ButtonStyle(color=ft.Colors.BLACK,
                                                        bgcolor=ft.Colors.ORANGE,
                                                        padding=10,
                                                        shape = ft.RoundedRectangleBorder(radius = 10),
                                                        text_style=ft.TextStyle(size=15))),
                                ft.TextButton("Volver", style=ft.ButtonStyle(color=ft.Colors.BLACK), on_click=open_menu)
                            ],
                        ),
                    ),
                ]
            )
        ]
    )