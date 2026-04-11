from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from core.avl import AVL
from core.bst import BST
from models.flight_record import FlightRecord
from models.nodes import TreeNode


_PRIORITY_MAP: dict[int, str] = {
	1: "ALTA",
	2: "MEDIA",
	3: "BAJA",
}


def _parse_priority(value: Any) -> str:
	if isinstance(value, int):
		return _PRIORITY_MAP.get(value, "MEDIA")

	text = str(value).strip().upper()
	if text in {"1", "ALTA"}:
		return "ALTA"
	if text in {"2", "MEDIA"}:
		return "MEDIA"
	if text in {"3", "BAJA"}:
		return "BAJA"
	return "MEDIA"


def _parse_alert(value: Any) -> str:
	if isinstance(value, bool):
		return "ALERTA" if value else "NORMAL"

	text = str(value).strip().upper()
	return text if text else "NORMAL"


def _parse_promotion(value: Any) -> float:
	if isinstance(value, bool):
		# El JSON del profesor usa promocion como booleano en modo insercion.
		# En el modelo interno lo representamos como valor numerico.
		return 0.0

	if value is None:
		return 0.0

	try:
		return float(value)
	except (TypeError, ValueError):
		return 0.0


def flight_record_from_dict(raw_flight: dict[str, Any]) -> FlightRecord:
	"""
	Convierte un objeto de vuelo JSON a FlightRecord estandar del proyecto.
	"""
	code_raw = raw_flight.get("codigo", raw_flight.get("code"))
	if code_raw is None:
		raise ValueError("El vuelo no contiene el campo 'codigo'.")

	base_price = float(raw_flight.get("precioBase", 0.0))

	record = FlightRecord(
		code_raw=code_raw,
		origin=str(raw_flight.get("origen", "")),
		destination=str(raw_flight.get("destino", "")),
		departure_time=str(raw_flight.get("horaSalida", "")),
		base_price=base_price,
		passengers=int(raw_flight.get("pasajeros", 0)),
		priority=_parse_priority(raw_flight.get("prioridad", "MEDIA")),
		promotion=_parse_promotion(raw_flight.get("promocion", 0.0)),
		alert=_parse_alert(raw_flight.get("alerta", "NORMAL")),
	)

	# Si vienen metadatos calculados en topologia, se preservan de forma inicial.
	if "precioFinal" in raw_flight:
		record.final_price = float(raw_flight.get("precioFinal", record.final_price))
	if "esCritico" in raw_flight:
		record.is_critical = bool(raw_flight.get("esCritico", record.is_critical))
	if "profundidad" in raw_flight:
		record.depth = int(raw_flight.get("profundidad", record.depth))
	if "altura" in raw_flight:
		record.height = int(raw_flight.get("altura", record.height))
	if "factorEquilibrio" in raw_flight:
		record.balance_factor = int(raw_flight.get("factorEquilibrio", record.balance_factor))

	return record


def _build_topology_node(raw_node: Optional[dict[str, Any]], parent: Optional[TreeNode] = None) -> Optional[TreeNode]:
	if raw_node is None:
		return None

	node = TreeNode(flight=flight_record_from_dict(raw_node), parent=parent)
	node.left = _build_topology_node(raw_node.get("izquierdo"), parent=node)
	node.right = _build_topology_node(raw_node.get("derecho"), parent=node)
	return node


def _count_nodes(node: Optional[TreeNode]) -> int:
	if node is None:
		return 0
	return 1 + _count_nodes(node.left) + _count_nodes(node.right)


def _load_insertion_mode(payload: dict[str, Any], critical_depth_limit: Optional[int]) -> tuple[AVL, BST]:
	flights = payload.get("vuelos")
	if not isinstance(flights, list):
		raise ValueError("El JSON de insercion debe incluir una lista en 'vuelos'.")

	avl = AVL(critical_depth_limit=critical_depth_limit)
	bst = BST()

	for raw_flight in flights:
		if not isinstance(raw_flight, dict):
			raise ValueError("Cada elemento de 'vuelos' debe ser un objeto JSON.")

		avl.insert(flight_record_from_dict(raw_flight))
		bst.insert(flight_record_from_dict(raw_flight))

	avl.refresh_metadata()
	bst.refresh_metadata()
	return avl, bst


def _load_topology_mode(payload: dict[str, Any], critical_depth_limit: Optional[int]) -> tuple[AVL, BST]:
	root_data = payload.get("raiz")

	avl = AVL(critical_depth_limit=critical_depth_limit)
	bst = BST()

	if root_data is None:
		return avl, bst

	if not isinstance(root_data, dict):
		raise ValueError("El campo 'raiz' debe ser un objeto JSON o null.")

	avl.root = _build_topology_node(root_data)
	bst.root = _build_topology_node(root_data)

	avl._size = _count_nodes(avl.root)  # pylint: disable=protected-access
	bst._size = _count_nodes(bst.root)  # pylint: disable=protected-access

	avl.refresh_metadata()
	bst.refresh_metadata()
	return avl, bst


def load_trees_from_payload(payload: dict[str, Any], critical_depth_limit: Optional[int] = None) -> dict[str, Any]:
	"""
	Carga AVL y BST desde un payload JSON en modo INSERCION o TOPOLOGIA.
	"""
	if not isinstance(payload, dict):
		raise ValueError("El contenido JSON debe ser un objeto en la raiz.")

	effective_critical_depth_limit = critical_depth_limit
	if effective_critical_depth_limit is None:
		effective_critical_depth_limit = payload.get("critical_depth_limit")

	mode = str(payload.get("tipo", "")).strip().upper()
	if mode == "INSERCION":
		avl, bst = _load_insertion_mode(payload, effective_critical_depth_limit)
	elif mode == "TOPOLOGIA":
		avl, bst = _load_topology_mode(payload, effective_critical_depth_limit)
	else:
		raise ValueError("El campo 'tipo' debe ser INSERCION o TOPOLOGIA.")

	return {
		"mode": mode,
		"avl": avl,
		"bst": bst,
		"node_count": avl.size(),
	}


def load_trees_from_json_file(file_path: str | Path, critical_depth_limit: Optional[int] = None) -> dict[str, Any]:
	"""
	Lee un archivo JSON y reconstruye los arboles segun su modo.
	"""
	path = Path(file_path)
	payload = json.loads(path.read_text(encoding="utf-8"))
	return load_trees_from_payload(payload, critical_depth_limit=critical_depth_limit)


def restore_avl_from_topology_payload(payload: dict[str, Any], critical_depth_limit: Optional[int] = None) -> AVL:
	"""
	Restaura un AVL desde un snapshot topologico.
	"""
	if payload.get("tipo") != "TOPOLOGIA":
		payload = {
			"tipo": "TOPOLOGIA",
			"raiz": payload.get("raiz", payload),
		}

	result = load_trees_from_payload(payload, critical_depth_limit=critical_depth_limit)
	return result["avl"]
