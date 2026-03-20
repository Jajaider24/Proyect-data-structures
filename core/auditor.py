from __future__ import annotations

from typing import Any

from core.avl import AVL
from core.bst import BST


def audit_bst_tree(tree: BST) -> dict[str, Any]:
	"""
	Auditoria basica para verificar propiedad BST y orden del inorder.
	"""
	inorder_keys = [flight.code_num for flight in tree.inorder()]
	sorted_ok = inorder_keys == sorted(inorder_keys)

	return {
		"is_valid_bst": tree.validate_bst_property() and sorted_ok,
		"bst_property_ok": tree.validate_bst_property(),
		"inorder_sorted_ok": sorted_ok,
		"node_count": tree.size(),
		"height": tree.height(),
	}


def audit_avl_tree(tree: AVL) -> dict[str, Any]:
	"""
	Reutiliza la auditoria nativa del AVL y agrega resumen de rotaciones.
	"""
	report = tree.audit_avl()
	report["rotations"] = tree.rotation_summary()
	return report


def audit_tree_pair(avl_tree: AVL, bst_tree: BST) -> dict[str, Any]:
	"""
	Ejecuta auditoria conjunta para vista comparativa.
	"""
	avl_report = audit_avl_tree(avl_tree)
	bst_report = audit_bst_tree(bst_tree)

	return {
		"avl": avl_report,
		"bst": bst_report,
		"summary": {
			"both_valid": bool(avl_report["is_valid_avl"] and bst_report["is_valid_bst"]),
			"avl_height": avl_report["tree_height"],
			"bst_height": bst_report["height"],
		},
	}
