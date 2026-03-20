from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from core.bst import BST
from services.serializer import tree_to_topology_payload


@dataclass
class UndoSnapshot:
	action: str
	payload: dict[str, Any]


class UndoManager:
	"""
	Maneja un historial de snapshots topologicos para deshacer cambios.
	"""

	def __init__(self, max_history: int = 100) -> None:
		self.max_history = max_history
		self._history: list[UndoSnapshot] = []

	def push_snapshot(self, tree: BST, action: str) -> None:
		snapshot = UndoSnapshot(action=action, payload=tree_to_topology_payload(tree))
		self._history.append(snapshot)

		if len(self._history) > self.max_history:
			self._history.pop(0)

	def can_undo(self) -> bool:
		return len(self._history) > 0

	def history_size(self) -> int:
		return len(self._history)

	def peek_snapshot(self) -> Optional[dict[str, Any]]:
		if not self._history:
			return None

		top = self._history[-1]
		return {
			"action": top.action,
			"payload": top.payload,
		}

	def pop_snapshot(self) -> Optional[dict[str, Any]]:
		if not self._history:
			return None

		top = self._history.pop()
		return {
			"action": top.action,
			"payload": top.payload,
		}

	def clear(self) -> None:
		self._history.clear()
