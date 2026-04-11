from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from api import state
from api.schemas import (
    CriticalDepthPayload,
    FlightPayload,
    FlightUpdatePayload,
    QueueProcessPayload,
    StressModePayload,
)
from controllers.audit_controller import audit_avl_tree, audit_tree_pair
from controllers.economics_controller import (
    calculate_tree_economics,
    least_profitable_flight,
    top_profitable_flights,
)
from controllers.metrics_controller import collect_tree_metrics, compare_tree_metrics
from models.normalization import normalize_flight_code
from services.json_loader import flight_record_from_dict, load_trees_from_payload
from services.serializer import tree_to_insertion_payload

router = APIRouter(prefix="/flights", tags=["flights"])


def _sync_bst_from_avl() -> None:
    payload = tree_to_insertion_payload(state.avl_tree)
    result = load_trees_from_payload(payload)
    state.bst_tree = result["bst"]


def _apply_flight_update(code: int, data: dict[str, object]) -> dict[str, object]:
    if state.avl_tree.search(code) is None:
        raise HTTPException(status_code=404, detail="No existe un vuelo con ese codigo")

    state.undo_manager.push_snapshot(state.avl_tree, action=f"update:{code}")

    state.avl_tree.delete(code)
    state.bst_tree.delete(code)

    try:
        avl_node = state.avl_tree.insert(flight_record_from_dict(data))
        state.bst_tree.insert(flight_record_from_dict(data))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "message": "Vuelo actualizado correctamente.",
        "updated_key": avl_node.key,
        "metrics": collect_tree_metrics(state.avl_tree),
    }


@router.get("/")
def list_flights() -> dict[str, object]:
    return {
        "count": state.avl_tree.size(),
        "flights": [flight.to_dict() for flight in state.avl_tree.inorder()],
    }


@router.post("/")
def create_flight(payload: FlightPayload) -> dict[str, object]:
    data = payload.model_dump()
    state.undo_manager.push_snapshot(state.avl_tree, action=f"insert:{data.get('codigo')}")

    try:
        avl_node = state.avl_tree.insert(flight_record_from_dict(data))
        state.bst_tree.insert(flight_record_from_dict(data))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "message": "Vuelo insertado correctamente.",
        "inserted_key": avl_node.key,
        "metrics": collect_tree_metrics(state.avl_tree),
    }


@router.put("/{code}")
def update_flight(code: str, payload: FlightUpdatePayload) -> dict[str, object]:
    try:
        code_key = normalize_flight_code(code)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    data = payload.model_dump()
    data["codigo"] = code
    return _apply_flight_update(code_key, data)


@router.delete("/{code}")
def delete_or_cancel_flight(code: int, mode: str = Query("ELIMINAR")) -> dict[str, object]:
    selected_mode = mode.strip().upper()
    if selected_mode not in {"ELIMINAR", "CANCELAR"}:
        raise HTTPException(status_code=400, detail="mode debe ser ELIMINAR o CANCELAR")

    state.undo_manager.push_snapshot(state.avl_tree, action=f"{selected_mode.lower()}:{code}")

    if selected_mode == "CANCELAR":
        removed_avl = state.avl_tree.cancel_subtree(code)
        removed_bst = state.bst_tree.cancel_subtree(code)

        if removed_avl == 0:
            raise HTTPException(status_code=404, detail="No existe un vuelo con ese codigo")

        return {
            "message": "Cancelacion masiva aplicada.",
            "removed_avl": removed_avl,
            "removed_bst": removed_bst,
            "metrics": collect_tree_metrics(state.avl_tree),
        }

    deleted_avl = state.avl_tree.delete(code)
    deleted_bst = state.bst_tree.delete(code)

    if not deleted_avl:
        raise HTTPException(status_code=404, detail="No existe un vuelo con ese codigo")

    return {
        "message": "Vuelo eliminado.",
        "deleted_avl": deleted_avl,
        "deleted_bst": deleted_bst,
        "metrics": collect_tree_metrics(state.avl_tree),
    }


@router.post("/queue")
def enqueue_flight(payload: FlightPayload) -> dict[str, object]:
    request_id = state.queue_manager.enqueue(payload.model_dump())
    return {
        "message": "Insercion agregada a la cola.",
        "request_id": request_id,
        "pending": state.queue_manager.pending_count(),
    }


@router.get("/queue")
def get_pending_queue() -> dict[str, object]:
    return {
        "pending": state.queue_manager.pending_count(),
        "items": state.queue_manager.list_pending(),
    }


@router.post("/queue/process")
def process_queue(payload: QueueProcessPayload) -> dict[str, object]:
    if state.queue_manager.pending_count() == 0:
        return {
            "message": "No hay inserciones pendientes.",
            "processed": [],
            "pending": 0,
        }

    state.undo_manager.push_snapshot(state.avl_tree, action="queue:process")

    try:
        processed = state.queue_manager.process_all(state.avl_tree, limit=payload.limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    _sync_bst_from_avl()

    return {
        "message": "Cola procesada.",
        "processed": processed,
        "pending": state.queue_manager.pending_count(),
        "metrics": collect_tree_metrics(state.avl_tree),
    }


@router.get("/metrics")
def get_metrics() -> dict[str, object]:
    return collect_tree_metrics(state.avl_tree)


@router.get("/economics")
def get_economics() -> dict[str, object]:
    return {
        "summary": calculate_tree_economics(state.avl_tree),
        "top_profitable": top_profitable_flights(state.avl_tree, limit=5),
    }


@router.post("/delete-least-profitable")
def delete_least_profitable() -> dict[str, object]:
    candidate = least_profitable_flight(state.avl_tree)
    if candidate is None:
        raise HTTPException(status_code=404, detail="No hay vuelos para eliminar")

    selected_key = int(candidate["codigoNormalizado"])
    state.undo_manager.push_snapshot(state.avl_tree, action=f"smart_delete:{selected_key}")

    removed_avl = state.avl_tree.cancel_subtree(selected_key)
    removed_bst = state.bst_tree.cancel_subtree(selected_key)

    if removed_avl == 0:
        raise HTTPException(
            status_code=409,
            detail="No se pudo completar la eliminacion inteligente por estado inconsistente",
        )

    return {
        "message": "Eliminacion inteligente aplicada.",
        "selected": candidate,
        "removed_avl": removed_avl,
        "removed_bst": removed_bst,
        "metrics": collect_tree_metrics(state.avl_tree),
    }


@router.get("/audit")
def get_avl_audit() -> dict[str, object]:
    return audit_avl_tree(state.avl_tree)


@router.get("/compare")
def compare_avl_vs_bst() -> dict[str, object]:
    return {
        "metrics": compare_tree_metrics(state.avl_tree, state.bst_tree),
        "audit": audit_tree_pair(state.avl_tree, state.bst_tree),
    }


@router.post("/stress-mode")
def toggle_stress_mode(payload: StressModePayload) -> dict[str, object]:
    state.avl_tree.set_stress_mode(payload.enabled)
    return {
        "message": "Modo estres actualizado.",
        "stress_mode": state.avl_tree.stress_mode,
        "metrics": collect_tree_metrics(state.avl_tree),
    }


@router.post("/critical-depth-limit")
def set_critical_depth_limit(payload: CriticalDepthPayload) -> dict[str, object]:
    state.avl_tree.set_critical_depth_limit(payload.limit)
    state.bst_tree.refresh_metadata(payload.limit)

    return {
        "message": "Profundidad critica actualizada.",
        "critical_depth_limit": payload.limit,
        "metrics": collect_tree_metrics(state.avl_tree),
    }


@router.post("/rebalance-global")
def rebalance_global() -> dict[str, object]:
    summary = state.avl_tree.rebalance_global()
    return {
        "message": "Rebalanceo global ejecutado.",
        "rotation_delta": summary,
        "metrics": collect_tree_metrics(state.avl_tree),
    }
