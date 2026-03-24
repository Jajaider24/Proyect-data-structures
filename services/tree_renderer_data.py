from __future__ import annotations

from collections import deque
from typing import Any, Optional

from core.bst import BST
from models.nodes import TreeNode


def _node_label(node: TreeNode) -> str:
	return f"{node.key} | h={node.flight.height} | bf={node.flight.balance_factor}"


def build_tree_renderer_data(tree: BST) -> dict[str, Any]:
	"""
	Convierte un arbol en una estructura simple de nodos y aristas para UI.
	"""
	if tree.root is None:
		return {
			"nodes": [],
			"edges": [],
			"root": None,
			"total_nodes": 0,
		}

	nodes: list[dict[str, Any]] = []
	edges: list[dict[str, int]] = []

	queue: deque[tuple[TreeNode, Optional[int], int]] = deque([(tree.root, None, 0)])

	while queue:
		node, parent_key, depth = queue.popleft()
		nodes.append(
			{
				"id": node.key,
				"label": _node_label(node),
				"depth": depth,
				"critical": node.flight.is_critical,
				"final_price": node.flight.final_price,
			}
		)

		if parent_key is not None:
			edges.append({"from": parent_key, "to": node.key})

		if node.left is not None:
			queue.append((node.left, node.key, depth + 1))
		if node.right is not None:
			queue.append((node.right, node.key, depth + 1))

	return {
		"nodes": nodes,
		"edges": edges,
		"root": tree.root.key,
		"total_nodes": len(nodes),
	}


def build_compare_renderer_data(avl_tree: BST, bst_tree: BST) -> dict[str, Any]:
	"""
	Devuelve datos de render para vista comparativa AVL vs BST.
	"""
	return {
		"avl": build_tree_renderer_data(avl_tree),
		"bst": build_tree_renderer_data(bst_tree),
	}
