import flet as ft
from metodos_vuelos import middleware
from datetime import date
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
# BUILD A TREE
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

    # Leaf Case
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

    # Leave a margin at the top so the root isn't cut off by the canvas.
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

    # Map rápido de nodos
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



def PanelAVL(page):
    page.title = "Panel AVL"
    button_style = ft.ButtonStyle(
            padding = 10,
            shape = ft.RoundedRectangleBorder(radius = 10),
            text_style=ft.TextStyle(size=15)
    )
    button_width = 200
    button_height = 50

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

    def refresh_tree():
        avl_nodes_refreshed, avl_edges_refreshed, _, _ = get_render_information()
        new_positions = compute_positions(avl_nodes_refreshed, avl_edges_refreshed)
        new_width, new_height = compute_canvas_size(new_positions)

        canvas_avl.shapes = draw_tree(avl_nodes_refreshed, avl_edges_refreshed, new_positions)
        canvas_avl.width = new_width
        canvas_avl.height = new_height
        page.update()

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


    async def open_menu(e):
        await page.push_route("/")

    async def open_form(e):
        await page.push_route("/formpanel")

    async def open_modify_form(e):
        await page.push_route("/modifypanel")

    def flights_code_capture():
        flights = middleware.get_flight_list()
        return [
            ft.DropdownOption(key=f['codigo'], text=f['codigo']) 
            for f in flights
        ]

    def search_flight(flights):
        return next((f for f in flights if f['codigo'] == codigo.value), None)

    def complete_text(e):
        flights = middleware.get_flight_list()
        flight_find = search_flight(flights)
        if flight_find:
            origen.value = "ORIGEN: " + flight_find['origen']
            destino.value = "DESTINO: " + flight_find['destino']
            hora.value = "HORA DE SALIDA: " + flight_find['horaSalida']
            precio.value = "PRECIO BASE: " + str(flight_find['precioBase'])
            pasajeros.value = "NÚMERO DE PASAJEROS: " + str(flight_find['pasajeros'])
            prioridad.value = "NIVEL DE PRIORIDAD: " + flight_find['prioridad']
    
    def clean_text():
        origen.value = "ORIGEN: "
        destino.value = "DESTINO : "
        hora.value = "HORA DE SALIDA: "
        precio.value = "PRECIO BASE: "
        pasajeros.value = "NÚMERO DE PASAJEROS: "
        prioridad.value = "NIVEL DE PRIORIDAD: "

    def delete_flight(mode):
        if(codigo.value is None):
            print("No se puede eliminar o cancelar un árbol vacio")
        else:
            flights = middleware.get_flight_list()
            flight_find = search_flight(flights)
            middleware.delete_flight(flight_find["codigoNormalizado"], mode)
            page.pop_dialog()
            page.pop_dialog()
            codigo.options = flights_code_capture()
            clean_text()
            refresh_tree()

    def apply_intelligent_delete(e=None):
        result = middleware.delete_least_profitable()
        if result is None:
            return

        codigo.options = flights_code_capture()
        clean_text()
        refresh_tree()

    def undo_action(e=None):
        result = middleware.undo_last_action()
        if result is None:
            return
        codigo.options = flights_code_capture()
        clean_text()
        refresh_tree()

    def redo_action(e=None):
        result = middleware.redo_last_action()
        if result is None:
            return
        codigo.options = flights_code_capture()
        clean_text()
        refresh_tree()

    def get_version_options():
        versions_payload = middleware.list_versions()
        if not versions_payload:
            return []

        versions = versions_payload.get("versions", [])
        return [
            ft.DropdownOption(key=item.get("name", ""), text=item.get("name", ""))
            for item in versions
            if item.get("name")
        ]

    selected_version = ft.Dropdown(
        label="Version",
        width=button_width,
        options=get_version_options(),
    )

    def open_restore_modal(e=None):
        selected_version.options = get_version_options()
        if not selected_version.options:
            selected_version.value = None
        page.show_dialog(restore_modal)
        page.update()

    def restore_selected_version(e=None):
        if not selected_version.value:
            return

        restored = middleware.restore_version(selected_version.value)
        if restored is None:
            return

        page.pop_dialog()
        codigo.options = flights_code_capture()
        clean_text()
        refresh_tree()

    restore_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Restaurar Version"),
        content=ft.Column(controls=[selected_version], tight=True),
        actions=[
            ft.TextButton("CONFIRMAR", on_click=restore_selected_version),
            ft.TextButton("SALIR", on_click=lambda e: page.pop_dialog()),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    metrics_text = ft.TextField(
        value="",
        read_only=True,
        multiline=True,
        min_lines=10,
        max_lines=18,
        width=560,
        border_color=ft.Colors.BLUE,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
    )

    metrics_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Metricas del Arbol AVL"),
        content=ft.Column(controls=[metrics_text], tight=True),
        actions=[
            ft.TextButton("Cerrar", on_click=lambda e: page.pop_dialog()),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def show_metrics(e=None):
        metrics = middleware.get_metrics()
        if metrics is None:
            return

        depth_traversal = metrics.get("depth_traversal", {})
        rotations = metrics.get("rotations", {})
        lines = [
            f"Raiz: {metrics.get('root')}",
            f"Altura: {metrics.get('height')}",
            f"Hojas: {metrics.get('leaf_count')}",
            f"Nodos: {metrics.get('node_count')}",
            f"Modo Estres: {metrics.get('stress_mode', False)}",
            "",
            "Recorridos:",
            f"- Preorder: {depth_traversal.get('preorder', [])}",
            f"- Inorder: {depth_traversal.get('inorder', [])}",
            f"- Postorder: {depth_traversal.get('postorder', [])}",
            f"- Anchura: {metrics.get('breadth_traversal', [])}",
        ]

        if rotations:
            lines.extend(
                [
                    "",
                    "Rotaciones:",
                    f"- LL: {rotations.get('LL', 0)}",
                    f"- RR: {rotations.get('RR', 0)}",
                    f"- LR: {rotations.get('LR', 0)}",
                    f"- RL: {rotations.get('RL', 0)}",
                    f"- Simples Izquierda: {rotations.get('simple_left', 0)}",
                    f"- Simples Derecha: {rotations.get('simple_right', 0)}",
                    f"- Simples Total: {rotations.get('simple_total', 0)}",
                    f"- Cancelaciones Masivas: {rotations.get('mass_cancellations', 0)}",
                ]
            )

        metrics_text.value = "\n".join(lines)
        page.show_dialog(metrics_modal)
        page.update()
    

    codigo=ft.Dropdown(
        editable=True,
        label="Codigo",
        options=flights_code_capture(),
        on_select = complete_text,
        )
    
    modal_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Seleccione el Vuelo a Eliminar"),
        content = ft.Column(controls = [codigo,
                                        origen,
                                        destino,
                                        hora,
                                        precio,
                                        pasajeros,
                                        prioridad,]),
        actions=[
            ft.TextButton("CANCELAR", on_click=lambda e: page.show_dialog(confirm_cancel_dialog)),
            ft.TextButton("ELIMINAR", on_click=lambda e: page.show_dialog(confirm_dialog)),
            ft.TextButton("SALIR", on_click=lambda e: page.pop_dialog()),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: print("Modal dialog dismissed!"),
    )

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("¿Esta Seguro que Desea Eliminar este Vuelo?"),
        actions=[
            ft.TextButton("CONFIRMAR", on_click=lambda e: delete_flight("ELIMINAR")),
            ft.TextButton("SALIR", on_click=lambda e: page.pop_dialog()),
        ],
    )

    confirm_cancel_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("¿Esta Seguro que Desea Cancelar este Vuelo?"),
        actions=[
            ft.TextButton("CONFIRMAR", on_click=lambda e: delete_flight("CANCELAR")),
            ft.TextButton("SALIR", on_click=lambda e: page.pop_dialog()),
        ],
    )

    async def handle_save_file(e: ft.Event[ft.Button]):
        default_name = f"vuelos_version_{date.today()}"
        path_destino = await ft.FilePicker().save_file(
            file_name=f"{nombre.value}.json" if nombre.value != "" else default_name,
            allowed_extensions=["json"]
        )
        page.pop_dialog()
        if path_destino:
            saved = middleware.save_tree_topology_file(path_destino)
            if saved is None:
                return

            print(f"Archivo guardado en: {path_destino}")
            if nombre.value != "":
                middleware.save_version(nombre.value, sobreescribir.value)
            else:
                middleware.save_version(default_name, sobreescribir.value)

    nombre = ft.TextField(label = "Nombre de la Version", hint_text = "Ingrese el Nombre")
    sobreescribir = ft.Switch(label="Sobreescribir", value=False, label_text_style=ft.TextStyle(color = ft.Colors.WHITE, size = 15))
    
    save_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Ingrese el nombre de la versión"),
        content = ft.Column(controls = [
            nombre,
            sobreescribir
        ]),
        actions=[
            ft.TextButton("CONFIRMAR", on_click = handle_save_file),
            ft.TextButton("SALIR", on_click=lambda e: page.pop_dialog()),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: print("Modal dialog dismissed!"),
    )

    # Left Container (70%) and Right Container (30%)
    return ft.View(
        route="/panelavl",
        padding=0, # Remove the window's outer borders
        controls=[
            ft.Row(
                expand=True, # Allow containers to use expand=7 and expand=3
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
                            scroll = ft.ScrollMode.ALWAYS,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Button("Crear Vuelo", width=button_width, height=button_height, style=button_style, on_click=open_form),
                                ft.Button("Modificar Vuelo", width=button_width, height=button_height, style=button_style, on_click=open_modify_form),
                                ft.Button("Eliminar/Cancelar", width=button_width, height=button_height, style=button_style, on_click=lambda e: page.show_dialog(modal_dialog),),
                                ft.Button("Guardar Árbol", width=button_width, height=button_height, style=button_style, on_click=lambda e: page.show_dialog(save_modal)),
                                ft.Button("Eliminación Inteligente", width=button_width, height=button_height, style=button_style, on_click=apply_intelligent_delete),
                                ft.Button("Retroceso", width=button_width, height=button_height, style=button_style, on_click=undo_action),
                                ft.Button("Redo", width=button_width, height=button_height, style=button_style, on_click=redo_action),
                                ft.Button("Restaurar Versión", width=button_width, height=button_height, style=button_style, on_click=open_restore_modal),
                                ft.Button("Metricas", width=button_width, height=button_height, style=button_style, on_click=show_metrics),
                                ft.TextButton("Volver", style = ft.ButtonStyle(ft.Colors.BLACK), on_click=open_menu)
                            ],
                        ),
                    ),
                ]
            )
        ]
    )

origen = ft.Text("ORIGEN: ")
destino = ft.Text("DESTINO :")
hora = ft.Text("HORA DE SALIDA: ")
precio = ft.Text("PRECIO BASE: ")
pasajeros = ft.Text("NÚMERO DE PASAJEROS: ")
prioridad = ft.Text("NIVEL DE PRIORIDAD: ")

