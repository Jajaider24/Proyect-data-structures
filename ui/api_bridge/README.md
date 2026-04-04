# Capa intermedia UI -> API

Esta carpeta encapsula toda la comunicacion HTTP del frontend con el backend FastAPI.

## Componentes

- `client.py`: cliente `SkyBalanceApiClient` con un metodo por endpoint.
- `payloads.py`: clases para preparar/validar datos del frontend antes de enviar.
- `exceptions.py`: error controlado `ApiBridgeError` para manejar fallos de red/HTTP.

## Datos esperados para crear/encolar vuelo

Clase: `FlightFormData`

Campos requeridos:
- `codigo`
- `origen`
- `destino`
- `hora_salida`
- `precio_base`
- `pasajeros`

Campos opcionales:
- `prioridad` (`1|2|3` o `ALTA|MEDIA|BAJA`)
- `promocion` (`bool` o numero)
- `alerta` (`bool` o `ALERTA|NORMAL`)

Ejemplo:

```python
from api_bridge import FlightFormData

payload = FlightFormData(
    codigo="SB901",
    origen="Bogota",
    destino="Cali",
    hora_salida="14:00",
    precio_base="420",
    pasajeros="115",
    prioridad="1",
    promocion=False,
    alerta=False,
).to_api_payload()
```

## Ejemplo de uso desde un boton

```python
from api_bridge import ApiBridgeError, SkyBalanceApiClient, FlightFormData

client = SkyBalanceApiClient()

def on_click_crear_vuelo():
    try:
        payload = FlightFormData(
            codigo="SB901",
            origen="Bogota",
            destino="Cali",
            hora_salida="14:00",
            precio_base="420",
            pasajeros="115",
        ).to_api_payload()

        result = client.create_flight(payload)
        print("OK:", result)
    except ApiBridgeError as exc:
        print(f"API ERROR [{exc.status_code}]: {exc.detail}")
    except ValueError as exc:
        print(f"FORM ERROR: {exc}")
```

## Endpoints cubiertos en `SkyBalanceApiClient`

- Flights: listar, crear, eliminar/cancelar, cola, procesar cola, metricas, economics, audit, compare, stress, rebalance.
- Versions: guardar, listar, restaurar, eliminar.
- Trees: cargar archivo, exportar topology/insertion, exportar a archivo, undo.
- Health: verificar estado del backend.
