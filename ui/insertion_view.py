import flet as ft

def InsertionView(page):
    # Definimos el estilo una sola vez para reutilizarlo
    button_style = ft.ButtonStyle(
        bgcolor=ft.Colors.BLUE,
        color=ft.Colors.WHITE,
        shape=ft.RoundedRectangleBorder(radius=20),
        elevation=6,
        text_style=ft.TextStyle(size=15)
    )
    async def open_menu(e):
        await page.push_route("/")

    # Retornamos un objeto View
    return ft.View(
        route="/insertion", # La ruta que identifica a esta página
        padding=0,
        spacing=0,
        controls=[
            ft.Container(
                expand=True, # Ocupa todo el alto y ancho
                gradient=ft.LinearGradient(
                    begin=ft.Alignment.BOTTOM_CENTER,
                    end=ft.Alignment.TOP_CENTER,
                    colors=[ft.Colors.GREY, ft.Colors.LIGHT_BLUE],
                ),
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=30,
                    controls=[
                        ft.Container(
                            content=ft.Text(
                                "Sistema de Gestión de Vuelos", 
                                size=30, 
                                weight=ft.FontWeight.BOLD
                            ),
                            margin=ft.Margin.only(bottom=100),
                        ),
                        ft.Button( # Usamos ElevatedButton para que acepte el bgcolor del style
                            "Método Inserción",
                            width=200,
                            height=50,
                            style=button_style,
                            on_click=lambda _: page.push_route("/metodo_1") # Ejemplo de navegación
                        ),
                        ft.Button(
                            "Método Topología",
                            width=200,
                            height=50,
                            style=button_style,
                        ),
                        ft.TextButton(
                            "Volver",
                            style = ft.ButtonStyle(color = ft.Colors.BLACK),
                            on_click = open_menu
                        )
                    ]
                )
            )
        ]
    )