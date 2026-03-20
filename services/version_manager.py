from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from core.bst import BST
from services.serializer import tree_to_topology_payload


@dataclass
class StoredVersion:
	name: str
	created_at: str
	payload: dict[str, Any]


class VersionManager:
	"""
	Versionado manual del arbol: guardar, listar, restaurar y eliminar.
	"""

	def __init__(self) -> None:
		self._versions: dict[str, StoredVersion] = {}

	def save_version(self, name: str, tree: BST, overwrite: bool = False) -> dict[str, Any]:
		clean_name = name.strip()
		if not clean_name:
			raise ValueError("El nombre de la version no puede estar vacio.")

		if clean_name in self._versions and not overwrite:
			raise ValueError(f"La version '{clean_name}' ya existe.")

		version = StoredVersion(
			name=clean_name,
			created_at=datetime.now(timezone.utc).isoformat(),
			payload=tree_to_topology_payload(tree),
		)
		self._versions[clean_name] = version

		return {
			"name": version.name,
			"created_at": version.created_at,
		}

	def list_versions(self) -> list[dict[str, Any]]:
		ordered = sorted(self._versions.values(), key=lambda item: item.created_at)
		return [
			{
				"name": item.name,
				"created_at": item.created_at,
			}
			for item in ordered
		]

	def get_version_payload(self, name: str) -> Optional[dict[str, Any]]:
		version = self._versions.get(name)
		if version is None:
			return None
		return version.payload

	def delete_version(self, name: str) -> bool:
		if name not in self._versions:
			return False
		del self._versions[name]
		return True

	def clear(self) -> None:
		self._versions.clear()
