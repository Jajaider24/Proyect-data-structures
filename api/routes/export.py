from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api import state
from api.schemas import FilePathPayload
from services.json_loader import load_trees_from_json_file, load_trees_from_payload
from services.serializer import (
    save_tree_insertion,
    save_tree_topology,
    tree_to_insertion_payload,
    tree_to_topology_payload,
)

router = APIRouter(prefix="/trees", tags=["trees"])


@router.post("/load-file")
def load_from_json_file(payload: FilePathPayload) -> dict[str, object]:
    if state.avl_tree.size() > 0:
        state.undo_manager.push_snapshot(state.avl_tree, action="load_file")

    try:
        result = load_trees_from_json_file(payload.path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {payload.path}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    state.avl_tree = result["avl"]
    state.bst_tree = result["bst"]

    return {
        "message": "Arbol cargado desde archivo.",
        "mode": result["mode"],
        "node_count": result["node_count"],
    }


@router.get("/export/topology")
def export_topology() -> dict[str, object]:
    return tree_to_topology_payload(state.avl_tree)


@router.get("/export/insertion")
def export_insertion() -> dict[str, object]:
    return tree_to_insertion_payload(state.avl_tree)


@router.post("/export/topology-file")
def export_topology_to_file(payload: FilePathPayload) -> dict[str, object]:
    path = save_tree_topology(state.avl_tree, payload.path)
    return {
        "message": "Topologia exportada.",
        "path": str(path),
    }


@router.post("/export/insertion-file")
def export_insertion_to_file(payload: FilePathPayload) -> dict[str, object]:
    path = save_tree_insertion(state.avl_tree, payload.path)
    return {
        "message": "Inserciones exportadas.",
        "path": str(path),
    }


@router.post("/undo")
def undo_last_action() -> dict[str, object]:
    snapshot = state.undo_manager.pop_snapshot()
    if snapshot is None:
        raise HTTPException(status_code=404, detail="No hay acciones para deshacer")

    result = load_trees_from_payload(snapshot["payload"])
    state.avl_tree = result["avl"]
    state.bst_tree = result["bst"]

    return {
        "message": "Estado restaurado desde historial.",
        "restored_action": snapshot["action"],
        "node_count": state.avl_tree.size(),
    }
