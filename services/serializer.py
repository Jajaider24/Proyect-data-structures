from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.bst import BST
from models.flight_record import FlightRecord


def _priority_to_number(priority: str) -> int:
	value = str(priority).strip().upper()
	if value == "ALTA":
		return 1
	if value == "BAJA":
		return 3
	return 2


def _insertion_flight_payload(flight: FlightRecord) -> dict[str, Any]:
	promotion_value: float | bool
	if float(flight.promotion) == 0.0:
		promotion_value = False
	else:
		promotion_value = float(flight.promotion)

	return {
		"codigo": flight.code_raw,
		"origen": flight.origin,
		"destino": flight.destination,
		"horaSalida": flight.departure_time,
		"precioBase": flight.base_price,
		"pasajeros": flight.passengers,
		"prioridad": _priority_to_number(flight.priority),
		"promocion": promotion_value,
		"alerta": bool(flight.alert == "ALERTA"),
	}


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
		"vuelos": [_insertion_flight_payload(flight) for flight in tree.level_order()],
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
