import flet as ft
from flet import canvas

from metodos_vuelos import middleware


NODE_RADIUS = 36
TOP_MARGIN = 40
LEFT_MARGIN = 50
EDGE_SPACING = 80
LEVEL_HEIGHT = 95
CANVAS_PADDING = 60
MIN_CANVAS_WIDTH = 620
MIN_CANVAS_HEIGHT = 520


def build_tree(edges):
	"""Build an adjacency map from the edge list and detect the root node."""
	tree = {}
	children = set()

	for edge in edges:
		parent = edge["from"]
		child = edge["to"]
		tree.setdefault(parent, []).append(child)
		children.add(child)

	root = None
	for node in tree:
		# The root is the node that appears as a parent but never as a child.
		if node not in children:
			root = node
			break

	return tree, root


def compute_tree_layout(tree, root, x=0, y=0, dx=80, level_height=100, pos=None):
	"""Assign screen coordinates to each node using a recursive tree layout."""
	if pos is None:
		pos = {}

	children = tree.get(root, [])
	if not children:
		# Leaf nodes keep the current position and advance the horizontal cursor.
		pos[root] = (x, y)
		return x + dx, pos

	child_x = x
	child_positions = []

	for child in children:
		# Lay out each subtree from left to right and reuse the updated cursor.
		child_x, pos = compute_tree_layout(
			tree,
			child,
			child_x,
			y + level_height,
			dx,
			level_height,
			pos,
		)
		child_positions.append(pos[child][0])

	# Center the parent above its children so the drawing looks balanced.
	parent_x = (min(child_positions) + max(child_positions)) / 2
	pos[root] = (parent_x, y)
	return child_x, pos


def compute_positions(edges):
	"""Convert the edge list into pixel positions for every visible node."""
	tree, root = build_tree(edges)
	if root is None:
		return {}

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
	"""Resize the canvas so the full tree fits without clipping."""
	if not pos:
		return MIN_CANVAS_WIDTH, MIN_CANVAS_HEIGHT

	max_x = max(x for x, _ in pos.values())
	max_y = max(y for _, y in pos.values())
	width = max(MIN_CANVAS_WIDTH, int(max_x + CANVAS_PADDING + NODE_RADIUS))
	height = max(MIN_CANVAS_HEIGHT, int(max_y + CANVAS_PADDING + NODE_RADIUS))
	return width, height


def draw_tree(nodes, edges, pos):
	"""Create the canvas shapes used to render nodes and edges."""
	shapes = []
	node_map = {node["id"]: node for node in nodes}

	for edge in edges:
		# Draw one line per edge before drawing the nodes on top of it.
		x1, y1 = pos[edge["from"]]
		x2, y2 = pos[edge["to"]]
		shapes.append(
			canvas.Line(
				x1,
				y1,
				x2,
				y2,
				paint=ft.Paint(stroke_width=2, color=ft.Colors.BLACK_54),
			)
		)

	for node_id, (x, y) in pos.items():
		node = node_map[node_id]
		# Highlight critical nodes so they are easy to identify in the comparison.
		node_color = ft.Colors.RED_ACCENT_700 if node.get("critical") else ft.Colors.BLACK

		shapes.append(
			canvas.Circle(
				x,
				y,
				NODE_RADIUS,
				paint=ft.Paint(color=node_color),
			)
		)
		shapes.append(
			canvas.Text(
				x,
				y,
				node["label"],
				alignment=ft.Alignment.CENTER,
				style=ft.TextStyle(size=10, color=ft.Colors.WHITE),
			)
		)

	return shapes


def build_compare_view(page):
	"""Build the comparison page that renders AVL and BST side by side."""
	page.title = "Comparacion AVL vs BST"

	avl_title = ft.Text("AVL", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)
	bst_title = ft.Text("BST", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)

	avl_summary = ft.Text("", color=ft.Colors.BLACK)
	bst_summary = ft.Text("", color=ft.Colors.BLACK)

	avl_canvas = canvas.Canvas(width=MIN_CANVAS_WIDTH, height=MIN_CANVAS_HEIGHT, shapes=[])
	bst_canvas = canvas.Canvas(width=MIN_CANVAS_WIDTH, height=MIN_CANVAS_HEIGHT, shapes=[])

	def apply_canvas(canvas_control, nodes, edges):
		# Recompute positions and canvas size every time the data changes.
		positions = compute_positions(edges)
		width, height = compute_canvas_size(positions)
		canvas_control.shapes = draw_tree(nodes, edges, positions)
		canvas_control.width = width
		canvas_control.height = height

	def refresh_compare_view(e=None):
		# Pull the latest tree data and metrics from the middleware layer.
		avl_nodes, avl_edges, bst_nodes, bst_edges = middleware.render_information()
		compare_data = middleware.compare_metrics() or {}

		# Update both canvases with the current AVL and BST structures.
		apply_canvas(avl_canvas, avl_nodes, avl_edges)
		apply_canvas(bst_canvas, bst_nodes, bst_edges)

		avl_metrics = compare_data.get("metrics", {}).get("avl", {})
		bst_metrics = compare_data.get("metrics", {}).get("bst", {})

		# Summaries are kept short so the user can compare both trees at a glance.
		avl_summary.value = (
			f"Raiz: {avl_metrics.get('root')} | Altura: {avl_metrics.get('height')} | Hojas: {avl_metrics.get('leaf_count')}"
		)
		bst_summary.value = (
			f"Raiz: {bst_metrics.get('root')} | Altura: {bst_metrics.get('height')} | Hojas: {bst_metrics.get('leaf_count')}"
		)

		page.update()

	async def open_menu(e):
		# Navigate back to the main route used by the app.
		await page.push_route("/")

	refresh_compare_view()

	return ft.View(
		route="/drawpanel",
		padding=0,
		controls=[
			ft.Container(
				expand=True,
				gradient=ft.LinearGradient(
					begin=ft.Alignment.BOTTOM_CENTER,
					end=ft.Alignment.TOP_CENTER,
					colors=[
						ft.Colors.GREY,
						ft.Colors.LIGHT_BLUE,
					],
				),
				content=ft.Column(
					expand=True,
					spacing=10,
					controls=[
						ft.Row(
							alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
							controls=[
								ft.Text(
									"Comparacion Estructural AVL vs BST",
									size=24,
									weight=ft.FontWeight.BOLD,
									color=ft.Colors.BLACK,
								),
								ft.Row(
									controls=[
										ft.Button("Actualizar", on_click=refresh_compare_view),
										ft.TextButton("Volver", style = ft.ButtonStyle(color=ft.Colors.BLACK), on_click=open_menu),
									]
								),
							],
						),
						ft.Row(
							expand=True,
							controls=[
								ft.Container(
									expand=1,
									padding=10,
									content=ft.Column(
										expand=True,
										scroll=ft.ScrollMode.ALWAYS,
										controls=[
											avl_title,
											avl_summary,
											ft.Row(
												expand=True,
												scroll=ft.ScrollMode.ALWAYS,
												controls=[avl_canvas],
											),
										],
									),
								),
								ft.VerticalDivider(width=1, color=ft.Colors.BLACK26),
								ft.Container(
									expand=1,
									padding=10,
									content=ft.Column(
										expand=True,
										scroll=ft.ScrollMode.ALWAYS,
										controls=[
											bst_title,
											bst_summary,
											ft.Row(
												expand=True,
												scroll=ft.ScrollMode.ALWAYS,
												controls=[bst_canvas],
											),
										],
									),
								),
							],
						),
					],
				),
			)
		],
	)
