import flet as ft
from metodos_vuelos import middleware
from flet import canvas

NODE_RADIUS = 40
TOP_MARGIN = 40
LEFT_MARGIN = 50
EDGE_SPACING = 80
LEVEL_HEIGHT = 100
CANVAS_PADDING = 60
MIN_CANVAS_WIDTH = 800
MIN_CANVAS_HEIGHT = 600

# =========================
# CONSTRUIR ÁRBOL
# =========================
def build_tree(edges):
    tree = {}
    children = set()

    for e in edges:
        parent = e['from']
        child = e['to']

        tree.setdefault(parent, []).append(child)
        children.add(child)

    # Encontrar raíz (el que nunca es hijo)
    root = None
    for node in tree:
        if node not in children:
            root = node
            break

    return tree, root


# =========================
# LAYOUT PROFESIONAL (RECURSIVO)
# =========================
def compute_tree_layout(tree, root, x=0, y=0, dx=80, level_height=100, pos=None):
    if pos is None:
        pos = {}

    children = tree.get(root, [])

    # Caso hoja
    if not children:
        pos[root] = (x, y)
        return x + dx, pos

    # Procesar hijos
    child_x = x
    child_positions = []

    for child in children:
        child_x, pos = compute_tree_layout(
            tree,
            child,
            child_x,
            y + level_height,
            dx,
            level_height,
            pos
        )
        child_positions.append(pos[child][0])

    # Centrar nodo padre respecto a sus hijos
    min_x = min(child_positions)
    max_x = max(child_positions)
    parent_x = (min_x + max_x) / 2

    pos[root] = (parent_x, y)

    return child_x, pos


# =========================
# API DE POSICIONES
# =========================
def compute_positions(nodes, edges):
    tree, root = build_tree(edges)
    if root is None:
        return {}

    # Margen superior para que la raiz no quede recortada por el canvas.
    _, pos = compute_tree_layout(
        tree,
        root,
        x=LEFT_MARGIN,
        y=TOP_MARGIN,
        dx=EDGE_SPACING,
        level_height=LEVEL_HEIGHT,
    )
    return pos


def compute_canvas_size(pos):
    if not pos:
        return MIN_CANVAS_WIDTH, MIN_CANVAS_HEIGHT

    max_x = max(x for x, _ in pos.values())
    max_y = max(y for _, y in pos.values())
    width = max(MIN_CANVAS_WIDTH, int(max_x + CANVAS_PADDING + NODE_RADIUS))
    height = max(MIN_CANVAS_HEIGHT, int(max_y + CANVAS_PADDING + NODE_RADIUS))
    return width, height


# =========================
# DIBUJAR ÁRBOL
# =========================
def draw_tree(nodes, edges, pos):
    shapes = []

    # Map rápido de nodos
    node_map = {n['id']: n for n in nodes}

    # ---------------------
    # DIBUJAR ARISTAS
    # ---------------------
    for edge in edges:
        x1, y1 = pos[edge['from']]
        x2, y2 = pos[edge['to']]

        shapes.append(
            canvas.Line(
                x1, y1,
                x2, y2,
                paint=ft.Paint(stroke_width=2, color=ft.Colors.BLACK_54)
            )
        )

    # ---------------------
    # DIBUJAR NODOS
    # ---------------------
    for node_id, (x, y) in pos.items():
        node = node_map[node_id]

        shapes.append(
            canvas.Circle(
                x, y, NODE_RADIUS,
                paint=ft.Paint(color=ft.Colors.BLACK),
            )
        )

        shapes.append(
            canvas.Text(
                x, y,
                node['label'],
                alignment=ft.Alignment.CENTER,
                style=ft.TextStyle(size=10, color = ft.Colors.WHITE)
            )
        )

    return shapes

def PanelConcurrency(page):
    page.title = "Panel Simulación de Concurrencia"

    def get_render_information():
        return middleware.render_information()
    
    avl_nodes, avl_edges, bst_nodes, bst_edges = get_render_information()

    positions = compute_positions(avl_nodes, avl_edges)
    canvas_width, canvas_height = compute_canvas_size(positions)

    canvas_avl = canvas.Canvas(
        shapes=draw_tree(avl_nodes, avl_edges, positions),
        width=canvas_width,
        height=canvas_height
    )

    scrollable_canvas = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.ALWAYS,
        controls=[
            ft.Row(
                scroll=ft.ScrollMode.ALWAYS,
                controls=[canvas_avl],
            )
        ],
    )

    def refresh_tree():
        avl_nodes, avl_edges, _, _ = get_render_information()
        new_positions = compute_positions(avl_nodes, avl_edges)
        new_width, new_height = compute_canvas_size(new_positions)

        canvas_avl.shapes = draw_tree(avl_nodes, avl_edges, new_positions)
        canvas_avl.width = new_width
        canvas_avl.height = new_height
        page.update()

    async def open_menu(e):
        await page.push_route("/")


    limite = ft.TextField(label="Limite",  
                    width=textField_width, 
                    height=textField_height, 
                    hint_text="Ingrese el limite de colas a procesar",
                    )

    def process_queue(e=None):
        limit = limite.value
        page.pop_dialog()
        middleware.process_queue(limit)
        refresh_tree()

    limit_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Ingrese la cantidad de vuelos a procesar"),
            content = ft.Column(controls = [
                limite,
            ]),
            actions=[
                ft.TextButton("CONFIRMAR", on_click = process_queue),
                ft.TextButton("SALIR", on_click=lambda e: page.pop_dialog()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

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
                        expand=7,
                        alignment = ft.Alignment.CENTER,
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment.BOTTOM_CENTER,
                            end=ft.Alignment.TOP_CENTER,
                            colors=[
                                ft.Colors.WHITE,
                                ft.Colors.LIGHT_BLUE,
                            ]),
                        content=ft.Column(alignment=ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls = [ft.Text("ÁRBOL AVL DE VUELOS", 
                                                            style = ft.TextStyle(color = ft.Colors.BLACK, 
                                                                                weight=ft.FontWeight.BOLD)), 
                                                    scrollable_canvas]), 
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
                                codigo,
                                origen,
                                destino,
                                hora,
                                precio,
                                pasajeros,
                                prioridad,
                                promocion,
                                alerta,
                                ft.Button("Agregar a Cola", width = 150, height=50, style=ft.ButtonStyle(padding = 10,
                                                            shape = ft.RoundedRectangleBorder(radius = 10),
                                                            text_style=ft.TextStyle(size=15)), on_click = send_to_queue),
                                ft.Button("Procesar", width = 150, height=50, style=ft.ButtonStyle(color=ft.Colors.BLACK,
                                                        bgcolor=ft.Colors.ORANGE,
                                                        padding=10,
                                                        shape = ft.RoundedRectangleBorder(radius = 10),
                                                        text_style=ft.TextStyle(size=15)), on_click = lambda e: page.show_dialog(limit_modal)),
                                ft.TextButton("Volver", style=ft.ButtonStyle(color=ft.Colors.BLACK), on_click=open_menu)
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
                    hint_text="Ingrese la promoción",
                    hint_style=ft.TextStyle(color=ft.Colors.BLACK))

alerta = ft.Switch(label="   Alerta", 
                    value=False, 
                    label_text_style=ft.TextStyle(color = ft.Colors.BLACK, size = 15))

def send_to_queue():
    datos = {
        'code': codigo.value,
        'origin': origen.value,
        'destination': destino.value,
        'hour': hora.value,
        'price': precio.value,
        'passengers': pasajeros.value,
        'priority': prioridad.value,
        'discount': promocion.value,
        'alert': alerta.value,
    }
    middleware.enqueue(datos)

