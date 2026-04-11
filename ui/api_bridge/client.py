from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .exceptions import ApiBridgeError


@dataclass
class ApiClientConfig:
    base_url: str = "http://127.0.0.1:8000"
    timeout_seconds: float = 20.0


class SkyBalanceApiClient:
    """Cliente HTTP para consumir el backend FastAPI desde la UI."""

    def __init__(self, config: Optional[ApiClientConfig] = None) -> None:
        self.config = config or ApiClientConfig()

    # ---------------------------- Flights ----------------------------
    def list_flights(self) -> dict[str, Any]:
        return self._request("GET", "/flights/")

    def create_flight(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/flights/", body=payload)

    def update_flight(self, code: Any, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("PUT", f"/flights/{code}", body=payload)

    def delete_or_cancel_flight(self, code: int, mode: str = "ELIMINAR") -> dict[str, Any]:
        query = {"mode": mode}
        return self._request("DELETE", f"/flights/{int(code)}", query=query)

    def enqueue_flight(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/flights/queue", body=payload)

    def list_queue(self) -> dict[str, Any]:
        return self._request("GET", "/flights/queue")

    def process_queue(self, limit: Optional[int] = None) -> dict[str, Any]:
        return self._request("POST", "/flights/queue/process", body={"limit": limit})

    def get_metrics(self) -> dict[str, Any]:
        return self._request("GET", "/flights/metrics")

    def get_economics(self) -> dict[str, Any]:
        return self._request("GET", "/flights/economics")

    def delete_least_profitable(self) -> dict[str, Any]:
        return self._request("POST", "/flights/delete-least-profitable")

    def get_audit(self) -> dict[str, Any]:
        return self._request("GET", "/flights/audit")

    def compare_avl_vs_bst(self) -> dict[str, Any]:
        return self._request("GET", "/flights/compare")

    def set_stress_mode(self, enabled: bool) -> dict[str, Any]:
        return self._request("POST", "/flights/stress-mode", body={"enabled": bool(enabled)})

    def set_critical_depth_limit(self, limit: Optional[int]) -> dict[str, Any]:
        return self._request("POST", "/flights/critical-depth-limit", body={"limit": limit})

    def rebalance_global(self) -> dict[str, Any]:
        return self._request("POST", "/flights/rebalance-global")

    # ---------------------------- Versions ----------------------------
    def save_version(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/versions/save", body=payload)

    def list_versions(self) -> dict[str, Any]:
        return self._request("GET", "/versions/")

    def restore_version(self, name: str) -> dict[str, Any]:
        return self._request("POST", f"/versions/restore/{name}")

    def delete_version(self, name: str) -> dict[str, Any]:
        return self._request("DELETE", f"/versions/{name}")

    # ---------------------------- Trees ----------------------------
    def load_file(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/trees/load-file", body=payload)

    def export_topology(self) -> dict[str, Any]:
        return self._request("GET", "/trees/export/topology")

    def export_insertion(self) -> dict[str, Any]:
        return self._request("GET", "/trees/export/insertion")

    def export_topology_file(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/trees/export/topology-file", body=payload)

    def export_insertion_file(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/trees/export/insertion-file", body=payload)

    def get_render_data_compare(self) -> dict[str, Any]:
        """Obtiene datos de render para visualizar AVL y BST lado a lado."""
        return self._request("GET", "/trees/render-data/compare")

    def undo(self) -> dict[str, Any]:
        return self._request("POST", "/trees/undo")

    # ---------------------------- Health ----------------------------
    def health(self) -> dict[str, Any]:
        return self._request("GET", "/")

    # ---------------------------- Core HTTP ----------------------------
    def _request(
        self,
        method: str,
        path: str,
        *,
        body: Optional[dict[str, Any]] = None,
        query: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        url = self._build_url(path, query)

        payload_bytes: Optional[bytes] = None
        headers = {"Accept": "application/json"}
        if body is not None:
            payload_bytes = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(url=url, data=payload_bytes, method=method.upper(), headers=headers)

        try:
            with urlopen(request, timeout=self.config.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
                if not raw.strip():
                    return {}
                return json.loads(raw)
        except HTTPError as exc:
            error_payload = _decode_error_payload(exc)
            detail = _extract_detail(error_payload, fallback=str(exc))
            raise ApiBridgeError(status_code=exc.code, detail=detail, payload=error_payload) from exc
        except URLError as exc:
            raise ApiBridgeError(status_code=0, detail=f"Error de conexion: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise ApiBridgeError(status_code=0, detail="Respuesta no valida en formato JSON") from exc

    def _build_url(self, path: str, query: Optional[dict[str, Any]]) -> str:
        base = self.config.base_url.rstrip("/")
        route = path if path.startswith("/") else f"/{path}"

        if not query:
            return f"{base}{route}"

        clean_query = {k: v for k, v in query.items() if v is not None}
        encoded = urlencode(clean_query)
        if not encoded:
            return f"{base}{route}"
        return f"{base}{route}?{encoded}"


def _decode_error_payload(exc: HTTPError) -> Any:
    try:
        raw = exc.read().decode("utf-8")
    except Exception:
        return None

    if not raw.strip():
        return None

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def _extract_detail(payload: Any, fallback: str) -> str:
    if isinstance(payload, dict) and "detail" in payload:
        return str(payload["detail"])
    return fallback
