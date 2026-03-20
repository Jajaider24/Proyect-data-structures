from __future__ import annotations

from typing import Any

from core.bst import BST


def collect_tree_metrics(tree: BST) -> dict[str, Any]:
	"""
	Retorna un resumen de metricas estructurales y recorridos del arbol.
	"""
	level_order_keys = [flight.code_num for flight in tree.level_order()]
	preorder_keys = [flight.code_num for flight in tree.preorder()]
	inorder_keys = [flight.code_num for flight in tree.inorder()]
	postorder_keys = [flight.code_num for flight in tree.postorder()]

	metrics: dict[str, Any] = {
		"root": tree.root_key(),
		"height": tree.height(),
		"leaf_count": tree.leaf_count(),
		"node_count": tree.size(),
		"depth_traversal": {
			"preorder": preorder_keys,
			"inorder": inorder_keys,
			"postorder": postorder_keys,
		},
		"breadth_traversal": level_order_keys,
	}

	if hasattr(tree, "rotation_summary"):
		metrics["rotations"] = tree.rotation_summary()  # type: ignore[attr-defined]
	if hasattr(tree, "stress_mode"):
		metrics["stress_mode"] = bool(getattr(tree, "stress_mode"))

	return metrics


def compare_tree_metrics(avl_tree: BST, bst_tree: BST) -> dict[str, Any]:
	"""
	Compara dos arboles y destaca diferencias basicas de altura y hojas.
	"""
	avl_metrics = collect_tree_metrics(avl_tree)
	bst_metrics = collect_tree_metrics(bst_tree)

	avl_height = int(avl_metrics["height"])
	bst_height = int(bst_metrics["height"])

	return {
		"avl": avl_metrics,
		"bst": bst_metrics,
		"comparison": {
			"height_diff": bst_height - avl_height,
			"leaf_diff": int(bst_metrics["leaf_count"]) - int(avl_metrics["leaf_count"]),
			"is_avl_more_compact": avl_height <= bst_height,
		},
	}
