from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api import state
from api.schemas import VersionPayload
from services.json_loader import load_trees_from_payload

router = APIRouter(prefix="/versions", tags=["versions"])


@router.post("/save")
def save_version(payload: VersionPayload) -> dict[str, object]:
    try:
        info = state.version_manager.save_version(payload.name, state.avl_tree, overwrite=payload.overwrite)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "message": "Version guardada.",
        **info,
        "total_versions": len(state.version_manager.list_versions()),
    }


@router.get("/")
def list_versions() -> dict[str, object]:
    return {
        "total_versions": len(state.version_manager.list_versions()),
        "versions": state.version_manager.list_versions(),
    }


@router.post("/restore/{name}")
def restore_version(name: str) -> dict[str, object]:
    version_payload = state.version_manager.get_version_payload(name)
    if version_payload is None:
        raise HTTPException(status_code=404, detail="La version solicitada no existe")

    state.undo_manager.push_snapshot(state.avl_tree, action=f"restore_version:{name}")

    result = load_trees_from_payload(version_payload)
    state.avl_tree = result["avl"]
    state.bst_tree = result["bst"]

    return {
        "message": "Version restaurada.",
        "name": name,
        "node_count": state.avl_tree.size(),
    }


@router.delete("/{name}")
def delete_version(name: str) -> dict[str, object]:
    deleted = state.version_manager.delete_version(name)
    if not deleted:
        raise HTTPException(status_code=404, detail="La version solicitada no existe")

    return {
        "message": "Version eliminada.",
        "name": name,
        "total_versions": len(state.version_manager.list_versions()),
    }
