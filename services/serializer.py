from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.bst import BST


def tree_to_topology_payload(tree: BST) -> dict[str, Any]:
	"""
	Serializa el arbol en formato TOPOLOGIA.
	"""
	return {
		"tipo": "TOPOLOGIA",
		"raiz": tree.to_topology_dict(),
	}


def tree_to_insertion_payload(tree: BST) -> dict[str, Any]:
	"""
	Serializa el arbol en formato INSERCION (recorrido por niveles).
	"""
	return {
		"tipo": "INSERCION",
		"ordenamiento": "codigo",
		"vuelos": tree.to_insertion_list(),
	}


def save_payload(payload: dict[str, Any], file_path: str | Path) -> Path:
	"""
	Guarda un payload JSON en disco y retorna la ruta resultante.
	"""
	path = Path(file_path)
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
	return path


def load_payload(file_path: str | Path) -> dict[str, Any]:
	"""
	Carga y retorna un payload JSON desde disco.
	"""
	path = Path(file_path)
	return json.loads(path.read_text(encoding="utf-8"))


def save_tree_topology(tree: BST, file_path: str | Path) -> Path:
	"""
	Exporta y guarda el arbol en formato TOPOLOGIA.
	"""
	return save_payload(tree_to_topology_payload(tree), file_path)


def save_tree_insertion(tree: BST, file_path: str | Path) -> Path:
	"""
	Exporta y guarda el arbol en formato INSERCION.
	"""
	return save_payload(tree_to_insertion_payload(tree), file_path)
