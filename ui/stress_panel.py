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



def PanelStress(page):
    page.title = "Modo Estres"

    def get_render_information():
        return middleware.render_information()
    
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

    def format_audit_report(report):
        if not isinstance(report, dict):
            return "No se recibio informacion valida de auditoria."

        if report.get("error"):
            return "\n".join([
                "=== Error de Auditoria ===",
                f"Status_Code: {report.get('status_code', 'N/A')}",
                f"Detalle: {report.get('detail', 'Sin detalle')}",
            ])

        unbalanced = report.get("unbalanced_nodes") or []
        invalid_heights = report.get("invalid_height_nodes") or []
        issues = report.get("issues") or []
        rotations = report.get("rotations") or {}

        lines = [
            "RESUMEN GENERAL: ",
            "",
            f"AVL_Valido: {report.get('is_valid_avl', False)}",
            f"Propiedad_BST_OK: {report.get('bst_property_ok', False)}",
            f"Altura_del_Arbol: {report.get('tree_height', 0)}",
            f"Cantidad_de_Nodos: {report.get('node_count', 0)}",
            "",
            "NODOS DESBALANCEADOS: ",
            "",
            f"Total: {len(unbalanced)}",
            f"Nodos: {', '.join(str(n) for n in unbalanced) if unbalanced else 'Ninguno'}",
            "",
            "ROTACIONES ACUMULADAS: ",
            ""
            f"LL: {rotations.get('LL', 0)}",
            f"RR: {rotations.get('RR', 0)}",
            f"LR: {rotations.get('LR', 0)}",
            f"RL: {rotations.get('RL', 0)}",
            f"Simple_Izquierda: {rotations.get('simple_left', 0)}",
            f"Simple_Derecha: {rotations.get('simple_right', 0)}",
            f"Simple_Total: {rotations.get('simple_total', 0)}",
            f"Cancelaciones_Masivas: {rotations.get('mass_cancellations', 0)}",
            "",
            "ISSUES DETECTADOS ",
            "",
        ]

        if issues:
            for index, issue in enumerate(issues, start=1):
                lines.append(f"{index}. {issue}")
        else:
            lines.append("Ninguno")

        return "\n".join(lines)

    audit_text = ft.TextField(
        value="",
        read_only=True,
        multiline=True,
        min_lines=12,
        max_lines=20,
        width=560,
        border_color=ft.Colors.BLUE,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
    )

    audit_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Resultado Auditoria AVL"),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[audit_text],
            scroll=ft.ScrollMode.ALWAYS,
            tight=True,
        ),
        actions=[
            ft.TextButton("Cerrar", on_click=lambda e: page.pop_dialog()),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def audit_avl(e=None):
        report = middleware.audit_AVL()
        audit_text.value = format_audit_report(report)
        page.show_dialog(audit_modal)
        page.update()

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

    def global_rebalance(e=None):
        middleware.global_rebalance()
        refresh_tree()

    async def open_menu(e):
        global_rebalance(None)
        await page.push_route("/")

    async def open_create_flight(e):
        await page.push_route("/stressform")

    async def open_update_flight(e):
        await page.push_route("/updateflightstress")

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
                                        controls = [ft.Text("ÁRBOL DE VUELOS MODO ESTRES", 
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
                            controls=[
                                ft.Button("Crear Vuelo", width=button_width, height=button_height, style=button_style, on_click=open_create_flight),
                                ft.Button("Modificar Vuelo", width=button_width, height=button_height, style=button_style, on_click=open_update_flight),
                                ft.Button("Eliminar/Cancelar", width=button_width, height=button_height, style=button_style, on_click=lambda e: page.show_dialog(modal_dialog)),
                                ft.Button("Rebalanceo Global", width=button_width, height=button_height, style=button_style2, on_click=global_rebalance),
                                ft.Button("Auditoria AVL", width=button_width, height=button_height, style=button_style2, on_click=audit_avl),
                                ft.TextButton("Volver", style = ft.ButtonStyle(color = ft.Colors.BLACK),on_click=open_menu)
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