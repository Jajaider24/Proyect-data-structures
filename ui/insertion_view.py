import flet as ft
import json
from metodos_vuelos import middleware

def InsertionView(page):
    # We define the style once so we can reuse it
    async def open_menu(e):
        await page.push_route("/")
    
    async def handle_pick_files(e: ft.Event[ft.Button]):
        files = await ft.FilePicker().pick_files(allow_multiple=True)
        try:
            datos = vars(files[0])
            middleware.send_path_information(datos['path'])
            result = middleware.set_critical_depth_limit(critical_depth_input.value)

            if result is None:
                page.snack_bar = ft.SnackBar(
                    ft.Text("Arbol cargado, pero no se pudo aplicar la profundidad critica"),
                    bgcolor=ft.Colors.ORANGE_400,
                )
            else:
                page.snack_bar = ft.SnackBar(
                    ft.Text(
                        f"Arbol cargado con profundidad critica: {result.get('critical_depth_limit')}"
                    ),
                    bgcolor=ft.Colors.GREEN_400,
                )

            page.snack_bar.open = True
            page.update()
        except:
            print("No se ha seleccionado ningún archivo")
        finally:
            await open_menu(e)

    critical_depth_input = ft.TextField(
        label="Profundidad Critica",
        width=260,
        hint_text="Vacio = sin limite",
    )

    def apply_critical_depth_limit(e=None):
        result = middleware.set_critical_depth_limit(critical_depth_input.value)
        if result is None:
            page.snack_bar = ft.SnackBar(
                ft.Text("No se pudo actualizar la profundidad critica"),
                bgcolor=ft.Colors.RED_400,
            )
            page.snack_bar.open = True
            page.update()
            return

        page.snack_bar = ft.SnackBar(
            ft.Text(f"Profundidad critica actualizada: {result.get('critical_depth_limit')}"),
            bgcolor=ft.Colors.GREEN_400,
        )
        page.snack_bar.open = True
        page.update()


    insertionButton = ft.Button(  # We use ElevatedButton so that it adopts the background color from the style
                            "Árbol a Insertar",
                            width=260,
                            height=50,
                            style=button_style,
                            on_click=handle_pick_files
                        )
    
    # We return a View object
    return ft.View(
        route="/insertion", # The URL for this page
        padding=0,
        spacing=0,
        controls=[
            ft.Container(
                expand=True, # Occupies the entire height and width
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
                        critical_depth_input,
                        ft.Button(
                            "Aplicar Profundidad Critica",
                            width=260,
                            height=50,
                            style=button_style,
                            on_click=apply_critical_depth_limit,
                        ),
                        insertionButton,
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

button_style = ft.ButtonStyle(
    bgcolor=ft.Colors.BLUE,
    color=ft.Colors.WHITE,
    shape=ft.RoundedRectangleBorder(radius=20),
    elevation=6,
    text_style=ft.TextStyle(size=15)
)




