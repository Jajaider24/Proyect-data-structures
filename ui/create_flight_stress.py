import flet as ft
from metodos_vuelos import middleware
def StressForms(page):
    page.title = "Panel Captura Datos"

    async def open_stress_panel(e):
        await page.push_route("/stresspanel")

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=titulo,
        bgcolor = ft.Colors.GREEN,
        actions=[
            ft.TextButton("Aceptar", style = ft.ButtonStyle(ft.Colors.BLACK), on_click=lambda e: page.pop_dialog()),
        ],
    )

    def send_datos(e):
        try:
            datos = {
                'codigo': codigo.value,
                'origen': origen.value,
                'destino': destino.value,
                'horaSalida': hora.value,
                'precioBase': precio.value,
                'pasajeros': pasajeros.value,
                'prioridad': prioridad.value,
                'promocion': promocion.value,
                'alerta': alerta.value,
            }
            middleware.crear_vuelo(datos)
            limpiar_campos()
            titulo.value = "Vuelo Creado Correctamente"
            confirm_dialog.bgcolor = ft.Colors.GREEN
            page.show_dialog(confirm_dialog)
        except Exception as e: 
            error = str(f"Error al procesar el vuelo: {e}")
            titulo.value = error
            confirm_dialog.bgcolor = ft.Colors.RED
            page.show_dialog(confirm_dialog)
        

    def limpiar_campos():
        codigo.value = ''
        origen.value = ''
        destino.value = ''
        hora.value = ''
        precio.value = ''
        pasajeros.value = ''
        prioridad.value = ''
        promocion.value = ''
        alerta.value = False

    # Left Container (70%) and Right Container (30%)
    return ft.View(
        route="/stressform",
        padding=0, # Remove the outer borders of the window
        controls=[
            ft.Row(
                expand=True, # Allows containers to use `expand=7` and `expand=3`
                spacing=0,
                controls=[
                    # RIGHT PANEL (30%)
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
                            spacing=40,
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            scroll = ft.ScrollMode.ALWAYS,
                            expand = True,
                            controls=[
                                ft.Text("Ingrese los Datos del Vuelo", size = 20, weight=ft.FontWeight.BOLD),
                                ft.Row(alignment=ft.MainAxisAlignment.CENTER,
                                        controls = [codigo,
                                                    origen,
                                                    destino]
                                ),
                                ft.Row(alignment = ft.MainAxisAlignment.CENTER,
                                        controls = [hora,
                                                    precio,
                                                    pasajeros]
                                ),
                                ft.Row(alignment = ft.MainAxisAlignment.CENTER,
                                        controls = [prioridad,
                                                    promocion,
                                                    ft.Container(
                                                        content=alerta,
                                                        width=textField_width,
                                                        alignment=ft.Alignment.CENTER_LEFT,
                                                    )]
                                ),
                                ft.Button("Procesar", width = 150, height=50, style=ft.ButtonStyle(color=ft.Colors.BLACK,
                                                        bgcolor=ft.Colors.ORANGE,
                                                        padding=10,
                                                        shape = ft.RoundedRectangleBorder(radius = 10),
                                                        text_style=ft.TextStyle(size=15)), on_click=send_datos),
                                ft.TextButton("Volver", style=ft.ButtonStyle(color=ft.Colors.BLACK), on_click=open_stress_panel)
                            ],
                        ),
                    ),
                ]
            )
        ]
    )

textField_width = 220
textField_height = 50

codigo = ft.TextField(label="Código del Vuelo", 
            label_style = ft.TextStyle(color = ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
            cursor_color = ft.Colors.BLACK, 
            text_style= ft.TextStyle(color=ft.Colors.BLACK_87, weight=ft.FontWeight.BOLD),
            border_color = ft.Colors.BLACK, 
            width=textField_width, 
            height=textField_height, 
            hint_text="Ingrese el código", 
            hint_style=ft.TextStyle(color=ft.Colors.BLACK))

titulo=ft.Text("", color = ft.Colors.BLACK, weight=ft.FontWeight.BOLD)

origen = ft.TextField(label="Ciudad de Origen", 
        label_style = ft.TextStyle(color = ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
        cursor_color = ft.Colors.BLACK, 
        text_style= ft.TextStyle(color=ft.Colors.BLACK_87, weight=ft.FontWeight.BOLD), 
        border_color = ft.Colors.BLACK,
        width=textField_width, 
        height=textField_height,
        hint_text="Ingrese el Origen",
        hint_style=ft.TextStyle(color=ft.Colors.BLACK))

destino = ft.TextField(label="Ciudad de Destino",
        label_style = ft.TextStyle(color = ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
        cursor_color = ft.Colors.BLACK, 
        text_style= ft.TextStyle(color=ft.Colors.BLACK_87, weight=ft.FontWeight.BOLD),
        border_color = ft.Colors.BLACK,
        width=textField_width, 
        height=textField_height, 
        hint_text="Ingrese el Destino",
        hint_style=ft.TextStyle(color=ft.Colors.BLACK))

hora = ft.TextField(label="Hora de Salida", 
        label_style = ft.TextStyle(color = ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
        cursor_color = ft.Colors.BLACK, 
        text_style= ft.TextStyle(color=ft.Colors.BLACK_87, weight=ft.FontWeight.BOLD), 
        border_color = ft.Colors.BLACK,
        width=textField_width, 
        height=textField_height, 
        hint_text="Ingrese Hora de Salida",
        hint_style=ft.TextStyle(color=ft.Colors.BLACK))

precio = ft.TextField(label="Precio del Vuelo", 
        label_style = ft.TextStyle(color = ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
        cursor_color = ft.Colors.BLACK, 
        text_style= ft.TextStyle(color=ft.Colors.BLACK_87, weight=ft.FontWeight.BOLD), 
        border_color = ft.Colors.BLACK,
        width=textField_width, 
        height=textField_height, 
        hint_text="Ingrese el precio",
        hint_style=ft.TextStyle(color=ft.Colors.BLACK))

pasajeros = ft.TextField(label="Número de Pasajeros", 
        label_style = ft.TextStyle(color = ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
        cursor_color = ft.Colors.BLACK, 
        text_style= ft.TextStyle(color=ft.Colors.BLACK_87, weight=ft.FontWeight.BOLD), 
        border_color = ft.Colors.BLACK,
        width=textField_width, 
        height=textField_height, 
        hint_text="Número de Pasajeros",
        hint_style=ft.TextStyle(color=ft.Colors.BLACK))

prioridad = ft.TextField(label="Prioridad",  
        label_style = ft.TextStyle(color = ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
        cursor_color = ft.Colors.BLACK, 
        text_style= ft.TextStyle(color=ft.Colors.BLACK_87, weight=ft.FontWeight.BOLD), 
        border_color = ft.Colors.BLACK,
        width=textField_width, 
        height=textField_height, 
        hint_text="Ingrese la Prioridad",
        hint_style=ft.TextStyle(color=ft.Colors.BLACK))

promocion = ft.TextField(label="Promoción",  
        label_style = ft.TextStyle(color = ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
        cursor_color = ft.Colors.BLACK, 
        text_style= ft.TextStyle(color=ft.Colors.BLACK_87, weight=ft.FontWeight.BOLD), 
        border_color = ft.Colors.BLACK,
        width=textField_width, 
        height=textField_height, 
        hint_text="Ingrese la Promoción",
        hint_style=ft.TextStyle(color=ft.Colors.BLACK))

alerta = ft.Switch(label="   Alerta", value=False, label_text_style=ft.TextStyle(color = ft.Colors.BLACK, size = 15))
