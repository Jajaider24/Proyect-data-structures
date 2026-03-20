from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any, Optional

from core.avl import AVL
from services.json_loader import flight_record_from_dict


@dataclass
class QueuedInsertion:
	request_id: int
	flight_payload: dict[str, Any]


class InsertionQueueManager:
	"""
	Cola FIFO para programar y procesar inserciones de vuelos.
	"""

	def __init__(self) -> None:
		self._queue: deque[QueuedInsertion] = deque()
		self._next_request_id = 1

	def enqueue(self, flight_payload: dict[str, Any]) -> int:
		request_id = self._next_request_id
		self._next_request_id += 1

		self._queue.append(QueuedInsertion(request_id=request_id, flight_payload=flight_payload))
		return request_id

	def pending_count(self) -> int:
		return len(self._queue)

	def list_pending(self) -> list[dict[str, Any]]:
		return [
			{
				"request_id": item.request_id,
				"codigo": item.flight_payload.get("codigo"),
				"origen": item.flight_payload.get("origen", ""),
				"destino": item.flight_payload.get("destino", ""),
			}
			for item in self._queue
		]

	def process_next(self, avl_tree: AVL) -> Optional[dict[str, Any]]:
		if not self._queue:
			return None

		item = self._queue.popleft()
		flight = flight_record_from_dict(item.flight_payload)
		inserted = avl_tree.insert(flight)
		audit = avl_tree.audit_avl()

		return {
			"request_id": item.request_id,
			"inserted_code": inserted.key,
			"is_valid_avl": audit["is_valid_avl"],
			"conflict": len(audit["unbalanced_nodes"]) > 0,
		}

	def process_all(self, avl_tree: AVL, limit: Optional[int] = None) -> list[dict[str, Any]]:
		processed: list[dict[str, Any]] = []

		while self._queue and (limit is None or len(processed) < limit):
			result = self.process_next(avl_tree)
			if result is not None:
				processed.append(result)

		return processed

	def clear(self) -> None:
		self._queue.clear()
