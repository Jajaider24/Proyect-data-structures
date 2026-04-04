import flet as ft
from flet import canvas

# =========================
# DATOS (los tuyos)
# =========================
AVL_NODES = [
    {'id': 400, 'label': '400 | h=5 | bf=-1', 'depth': 0},
    {'id': 250, 'label': '250 | h=3 | bf=0', 'depth': 1},
    {'id': 600, 'label': '600 | h=4 | bf=-1', 'depth': 1},
    {'id': 150, 'label': '150 | h=2 | bf=0', 'depth': 2},
    {'id': 300, 'label': '300 | h=2 | bf=0', 'depth': 2},
    {'id': 500, 'label': '500 | h=2 | bf=0', 'depth': 2},
    {'id': 640, 'label': '640 | h=3 | bf=0', 'depth': 2},
    {'id': 120, 'label': '120 | h=1 | bf=0', 'depth': 3},
    {'id': 180, 'label': '180 | h=1 | bf=0', 'depth': 3},
    {'id': 270, 'label': '270 | h=1 | bf=0', 'depth': 3},
    {'id': 330, 'label': '330 | h=1 | bf=0', 'depth': 3},
    {'id': 450, 'label': '450 | h=1 | bf=0', 'depth': 3},
    {'id': 550, 'label': '550 | h=1 | bf=0', 'depth': 3},
    {'id': 620, 'label': '620 | h=2 | bf=0', 'depth': 3},
    {'id': 700, 'label': '700 | h=2 | bf=0', 'depth': 3},
    {'id': 610, 'label': '610 | h=1 | bf=0', 'depth': 4},
    {'id': 630, 'label': '630 | h=1 | bf=0', 'depth': 4},
    {'id': 650, 'label': '650 | h=1 | bf=0', 'depth': 4},
    {'id': 750, 'label': '750 | h=1 | bf=0', 'depth': 4},
]

AVL_EDGES = [
    {'from': 400, 'to': 250}, {'from': 400, 'to': 600},
    {'from': 250, 'to': 150}, {'from': 250, 'to': 300},
    {'from': 600, 'to': 500}, {'from': 600, 'to': 640},
    {'from': 150, 'to': 120}, {'from': 150, 'to': 180},
    {'from': 300, 'to': 270}, {'from': 300, 'to': 330},
    {'from': 500, 'to': 450}, {'from': 500, 'to': 550},
    {'from': 640, 'to': 620}, {'from': 640, 'to': 700},
    {'from': 620, 'to': 610}, {'from': 620, 'to': 630},
    {'from': 700, 'to': 650}, {'from': 700, 'to': 750},
]

NODE_RADIUS = 20
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
                paint=ft.Paint(stroke_width=2)
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
                paint=ft.Paint()
            )
        )

        shapes.append(
            canvas.Text(
                x, y,
                node['label'],
                alignment=ft.Alignment.CENTER,
                style=ft.TextStyle(size=10)
            )
        )

    return shapes

# =========================
# APP
# =========================
def draw_test(page):
    page.title = "AVL vs BST"

    positions = compute_positions(AVL_NODES, AVL_EDGES)
    canvas_width, canvas_height = compute_canvas_size(positions)

    canvas_avl = canvas.Canvas(
        shapes=draw_tree(AVL_NODES, AVL_EDGES, positions),
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

    return ft.View(
        route="/drawpanel",
        padding=0, # Elimina bordes externos de la ventana
        controls=[ft.Text("AVL Tree"),
        scrollable_canvas])
