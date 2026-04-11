from api_bridge import SkyBalanceApiClient
from api_bridge import (
    ApiBridgeError,
    CriticalDepthFormData,
    FilePathFormData,
    FlightFormData,
    FlightFormDataUpdate,
    SkyBalanceApiClient,
    TreeCompareRenderData,
    VersionFormData,
)

skybalance = SkyBalanceApiClient()

def crear_vuelo(datos):
    codigo = datos['codigo']
    origen = datos['origen']
    destino = datos['destino']
    hora_salida = datos['horaSalida']
    precio_base = datos['precioBase']
    pasajeros = datos['pasajeros']
    prioridad = datos['prioridad']
    promocion = datos['promocion']
    alerta = datos['alerta']
    flight = FlightFormData(codigo, origen, destino, hora_salida, precio_base, pasajeros, prioridad, promocion, alerta)
    try:
        skybalance.create_flight(flight.to_api_payload())
    except Exception as e:
        print("No se ha logrado Procesar el vuelo: ", e)

def send_path_information(datos):
    data = FilePathFormData(datos)
    try:
        skybalance.load_file(data.to_api_payload())
    except Exception as e:
        print("No se ha logrado procesar el archivo de vuelos: ", e)


def save_tree_insertion_file(path: str):
    data = FilePathFormData(path)
    try:
        return skybalance.export_insertion_file(data.to_api_payload())
    except Exception as e:
        print("No se ha logrado guardar el archivo de vuelos: ", e)
        return None

def get_flight_list():
    return skybalance.list_flights()['flights']

def modify_flight(datos):
    codigo = datos['codigo']
    origen = datos['origen']
    destino = datos['destino']
    hora_salida = datos['horaSalida']
    precio_base = datos['precioBase']
    pasajeros = datos['pasajeros']
    prioridad = datos['prioridad']
    promocion = datos['promocion']
    alerta = datos['alerta']
    flight = FlightFormDataUpdate(origen, destino, hora_salida, precio_base, pasajeros, prioridad, promocion, alerta)
    flight = flight.to_api_payload()
    try:
        skybalance.update_flight(codigo, flight)
    except Exception as e:
        print("No se ha logrado Procesar el vuelo: ", e)

def delete_flight(code, mode):
    if mode == "ELIMINAR":
        skybalance.delete_or_cancel_flight(code)
    elif mode == "CANCELAR":
        skybalance.delete_or_cancel_flight(code, mode)


def save_version(name, overwrite):
    save_payload = VersionFormData(name, overwrite)
    skybalance.save_version(save_payload.to_api_payload())
    print(skybalance.list_versions())


def list_versions():
    try:
        return skybalance.list_versions()
    except ApiBridgeError as e:
        print(f"Error HTTP {e.status_code}: {e.detail}")
        print("Payload error:", e.payload)
        return None


def restore_version(name):
    try:
        return skybalance.restore_version(name)
    except ApiBridgeError as e:
        print(f"Error HTTP {e.status_code}: {e.detail}")
        print("Payload error:", e.payload)
        return None


def undo_last_action():
    try:
        return skybalance.undo()
    except ApiBridgeError as e:
        print(f"Error HTTP {e.status_code}: {e.detail}")
        print("Payload error:", e.payload)
        return None


def get_metrics():
    try:
        return skybalance.get_metrics()
    except ApiBridgeError as e:
        print(f"Error HTTP {e.status_code}: {e.detail}")
        print("Payload error:", e.payload)
        return None

def enqueue(datos):
    flight_payload = FlightFormData(datos['code'], datos['origin'], datos['destination'], 
                                    datos['hour'], datos['price'], datos['passengers'], 
                                    datos['priority'], datos['discount'], datos['alert'])
    skybalance.enqueue_flight(flight_payload.to_api_payload())
    print(skybalance.list_queue())

def process_queue(limite):
    try:
        resp = skybalance.process_queue(None if limite == "" else int(limite))
        return resp
    except ApiBridgeError as e:
        print(f"Error HTTP {e.status_code}: {e.detail}")
        print("Payload error:", e.payload)
        return None
    
def get_list_queue():
    return skybalance.list_queue()

def render_information():
    response = skybalance.get_render_data_compare()
    avl_nodes = response["avl"]["nodes"]
    bst_nodes = response["bst"]["nodes"]
    avl_edges = response["avl"]["edges"]
    bst_edges = response["bst"]["edges"]
    return(avl_nodes, avl_edges, bst_nodes, bst_edges)


def compare_metrics():
    try:
        return skybalance.compare_avl_vs_bst()
    except ApiBridgeError as e:
        print(f"Error HTTP {e.status_code}: {e.detail}")
        print("Payload error:", e.payload)
        return None

def set_stress_mode(boolean_resp):
    return skybalance.set_stress_mode(boolean_resp)


def set_critical_depth_limit(limit):
    payload = CriticalDepthFormData(limit)
    try:
        return skybalance.set_critical_depth_limit(payload.to_api_payload()["limit"])
    except (ApiBridgeError, ValueError) as e:
        print("No se ha logrado actualizar la profundidad critica: ", e)
        return None

def global_rebalance():
    return skybalance.rebalance_global()


def delete_least_profitable():
    try:
        return skybalance.delete_least_profitable()
    except ApiBridgeError as e:
        print(f"Error HTTP {e.status_code}: {e.detail}")
        print("Payload error:", e.payload)
        return None

def audit_AVL():
    try:
        return skybalance.get_audit()
    except ApiBridgeError as e:
        print(f"Error HTTP {e.status_code}: {e.detail}")
        print("Payload error:", e.payload)
        return {
            "error": True,
            "status_code": e.status_code,
            "detail": e.detail,
            "payload": e.payload,
        }