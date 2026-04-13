import flet as ft
from metodos_vuelos import middleware
from flet import canvas
import asyncio

NODE_RADIUS = 40
TOP_MARGIN = 40
LEFT_MARGIN = 50
EDGE_SPACING = 80
LEVEL_HEIGHT = 100
CANVAS_PADDING = 60
MIN_CANVAS_WIDTH = 800
MIN_CANVAS_HEIGHT = 600

# =========================
# BUILD TREE
# =========================
def build_tree(edges):
    tree = {}
    children = set()

    for e in edges:
        parent = e['from']
        child = e['to']

        tree.setdefault(parent, []).append(child)
        children.add(child)

    # Finding one's roots (the one who is never a child)
    root = None
    for node in tree:
        if node not in children:
            root = node
            break

    return tree, root


# =========================
# PROFESSIONAL LAYOUT (RECURSIVE)
# =========================
def compute_tree_layout(tree, root, x=0, y=0, dx=80, level_height=100, pos=None):
    if pos is None:
        pos = {}

    children = tree.get(root, [])

    # Case leaf
    if not children:
        pos[root] = (x, y)
        return x + dx, pos

    # Process children
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

    # Center the parent node relative to its children
    min_x = min(child_positions)
    max_x = max(child_positions)
    parent_x = (min_x + max_x) / 2

    pos[root] = (parent_x, y)

    return child_x, pos


# =========================
# POSITIONS API
# =========================
def compute_positions(nodes, edges):
    tree, root = build_tree(edges)
    if root is None:
        return {}

    # Leave a margin at the top so that the root isn't cut off by the canvas.
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
# DRAW TREE
# =========================
def draw_tree(nodes, edges, pos):
    shapes = []

    # Create a mapping from node IDs to node data for easy access when drawing.
    node_map = {n['id']: n for n in nodes}

    # ---------------------
    # DRAW EDGES
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
    # DRAW NODES
    # ---------------------
    for node_id, (x, y) in pos.items():
        node = node_map[node_id]
        node_color = ft.Colors.RED_ACCENT_700 if node.get("critical") else ft.Colors.BLACK

        shapes.append(
            canvas.Circle(
                x, y, NODE_RADIUS,
                paint=ft.Paint(color=node_color),
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

    async def process_queue(e=None):
        limit = middleware.get_list_queue()['pending']
        for _ in range(limit):
            middleware.process_queue(1)
            refresh_tree()
            await asyncio.sleep(5)
    
    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=titulo,
        bgcolor = ft.Colors.GREEN,
        actions=[
            ft.TextButton("Aceptar", style = ft.ButtonStyle(ft.Colors.BLACK), on_click=lambda e: page.pop_dialog()),
        ],
    )

    def send_to_queue():
        try:
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
            limpiar_campos()
            titulo.value = "Vuelo Agregado Correctamente a la Cola"
            confirm_dialog.bgcolor = ft.Colors.GREEN
            page.show_dialog(confirm_dialog)
        except Exception as e:
            error = str(f"Error al Encolar el Vuelo: {e}")
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
        route="/concurrencypanel",
        padding=0, # Remove the outer borders of the window
        controls=[
            ft.Row(
                expand=True, # Allows containers to use `expand=7` and `expand=3`
                spacing=0,
                controls=[
                    # LEFT PANEL (70%)
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
                                                        text_style=ft.TextStyle(size=15)), on_click = process_queue),
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

titulo=ft.Text("", color = ft.Colors.BLACK, weight=ft.FontWeight.BOLD)
