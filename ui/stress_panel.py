import flet as ft

def PanelStress(page):
    page.title = "Modo Estres"
    button_style = ft.ButtonStyle(
            padding = 10,
            shape = ft.RoundedRectangleBorder(radius = 10),
            text_style=ft.TextStyle(size=15)
    )
    button_style2 = ft.ButtonStyle(
        color = ft.Colors.BLACK,
        bgcolor = ft.Colors.ORANGE,
        padding = 10,
        shape = ft.RoundedRectangleBorder(radius = 10),
        text_style=ft.TextStyle(size=15)
    )
    button_width = 200
    button_height = 50
    async def open_menu(e):
        await page.push_route("/")

    # Contenedor Izquierdo (70%) y Derecho (30%)
    return ft.View(
        route="/stresspanel",
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
                            controls=[
                                ft.Button("Crear Vuelo", width=button_width, height=button_height, style=button_style),
                                ft.Button("Modificar Vuelo", width=button_width, height=button_height, style=button_style),
                                ft.Button("Eliminar Vuelo", width=button_width, height=button_height, style=button_style),
                                ft.Button("Cancelar Vuelo", width=button_width, height=button_height, style=button_style),
                                ft.Button("Rebalanceo Global", width=button_width, height=button_height, style=button_style2),
                                ft.Button("Auditoria AVL", width=button_width, height=button_height, style=button_style2),
                                ft.TextButton("Volver", style = ft.ButtonStyle(color = ft.Colors.BLACK),on_click=open_menu)
                            ],
                        ),
                    ),
                ]
            )
        ]
    )