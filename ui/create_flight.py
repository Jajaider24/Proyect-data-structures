import flet as ft
from metodos_vuelos import middleware
def PanelForms(page):
    page.title = "Panel Captura Datos"

    async def open_avl(e):
        await page.push_route("/panelavl")

    # Contenedor Izquierdo (70%) y Derecho (30%)
    return ft.View(
        route="/formpanel",
        padding=0, # Elimina bordes externos de la ventana
        controls=[
            ft.Row(
                expand=True, # Permite que los contenedores usen expand=7 y expand=3
                spacing=0,
                controls=[
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
                                ft.TextButton("Volver", style=ft.ButtonStyle(color=ft.Colors.BLACK), on_click=open_avl)
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

def send_datos(e):
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
    limpiar_campos()
    middleware.crear_vuelo(datos)

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