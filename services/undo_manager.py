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
	It maintains topological snapshots to support undo/redo changes.
	"""

	def __init__(self, max_history: int = 100) -> None:
		self.max_history = max_history
		self._history: list[UndoSnapshot] = []
		self._redo_history: list[UndoSnapshot] = []

	def _append_limited(self, target: list[UndoSnapshot], snapshot: UndoSnapshot) -> None:
		target.append(snapshot)

		if len(target) > self.max_history:
			target.pop(0)

	def push_snapshot(self, tree: BST, action: str, clear_redo: bool = True) -> None:
		snapshot = UndoSnapshot(action=action, payload=tree_to_topology_payload(tree))
		self._append_limited(self._history, snapshot)

		if clear_redo:
			self.clear_redo()

	def push_redo_snapshot(self, tree: BST, action: str) -> None:
		snapshot = UndoSnapshot(action=action, payload=tree_to_topology_payload(tree))
		self._append_limited(self._redo_history, snapshot)

	def can_undo(self) -> bool:
		return len(self._history) > 0

	def can_redo(self) -> bool:
		return len(self._redo_history) > 0

	def history_size(self) -> int:
		return len(self._history)

	def redo_history_size(self) -> int:
		return len(self._redo_history)

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

	def pop_redo_snapshot(self) -> Optional[dict[str, Any]]:
		if not self._redo_history:
			return None

		top = self._redo_history.pop()
		return {
			"action": top.action,
			"payload": top.payload,
		}

	def clear_redo(self) -> None:
		self._redo_history.clear()

	def clear(self) -> None:
		self._history.clear()
		self._redo_history.clear()
