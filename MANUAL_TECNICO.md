# Manual Tecnico

## 1. Descripcion general

SkyBalance AVL implementa un sistema de gestion de vuelos con arquitectura por capas.

Nucleo:

- AVL para operacion principal balanceada.
- BST para comparacion estructural.

Capas:

- `core`: estructuras de datos.
- `models`: entidades de dominio.
- `controllers`: logica analitica y de auditoria.
- `services`: carga, serializacion, cola, versionado, undo.
- `api`: exposicion HTTP (FastAPI).
- `ui`: cliente Flet y middleware de integracion.
- `tests`: pruebas unitarias de requisitos criticos.

## 2. Arquitectura

### 2.1 Backend

- Framework: FastAPI.
- Estado en memoria: `api/state.py`.
- Rutas:
  - `api/routes/flights.py`
  - `api/routes/export.py`
  - `api/routes/versions.py`

### 2.2 Frontend

- Framework: Flet.
- Entrada principal: `ui/main.py`.
- Integracion con API: `ui/api_bridge/client.py` + `ui/metodos_vuelos/middleware.py`.

## 3. Modelo de datos

### 3.1 FlightRecord (`models/flight_record.py`)

Campos relevantes:

- Identidad: `code_raw`, `code_num`.
- Operacion: `origin`, `destination`, `departure_time`, `passengers`.
- Negocio: `base_price`, `promotion`, `final_price`, `priority`, `alert`.
- Arbol: `depth`, `height`, `balance_factor`, `is_critical`.

Reglas de negocio:

- Penalizacion critica: 25% sobre `base_price`.
- Rentabilidad: `pasajeros * precioFinal - promocion + penalizacion`.

### 3.2 TreeNode (`models/nodes.py`)

Contenedor de `FlightRecord` con enlaces `left`, `right`, `parent`.

## 4. Estructuras de datos

### 4.1 BST (`core/bst.py`)

- Insercion y busqueda por clave normalizada.
- Eliminacion clasica (0, 1 o 2 hijos).
- Cancelacion de subarbol.
- Recorridos: inorder, preorder, postorder y level-order.
- Recalculo global de metadatos.

### 4.2 AVL (`core/avl.py`)

- Insercion y eliminacion con rebalanceo.
- Rotaciones LL, RR, LR, RL.
- Modo estres (sin rebalanceo inmediato).
- Rebalanceo global.
- Auditoria AVL.
- Contadores de rotaciones y cancelaciones masivas.

## 5. Componentes de servicios

### 5.1 Carga/serializacion

- `services/json_loader.py`: reconstruccion desde JSON en modo `INSERCION` y `TOPOLOGIA`.
- `services/serializer.py`: exportacion de topologia e insercion.

### 5.2 Undo y versionado

- `services/undo_manager.py`: snapshots topologicos para retroceso.
- `services/version_manager.py`: guardar, listar, restaurar y eliminar versiones.

### 5.3 Cola de inserciones

- `services/queue_manager.py`: encolado y procesamiento por lotes.
- `core/queue.py`: implementacion FIFO.

### 5.4 Render de arboles

- `services/tree_renderer_data.py`: nodos/aristas para UI y comparativa AVL/BST.

## 6. Controladores

### 6.1 metrics_controller

- Metricas estructurales del arbol.
- Comparativa AVL vs BST.

### 6.2 economics_controller

- Resumen economico global.
- Top de vuelos por rentabilidad.
- Seleccion de menor rentabilidad con desempates.

### 6.3 audit_controller

- Validacion BST.
- Auditoria AVL con inconsistencias y resumen combinado.

## 7. API REST

### 7.1 Rutas de vuelos

Base: `/flights`

- `GET /` listar vuelos.
- `POST /` crear vuelo.
- `PUT /{code}` editar vuelo.
- `DELETE /{code}?mode=ELIMINAR|CANCELAR` eliminar/cancelar.
- `POST /queue` encolar insercion.
- `GET /queue` listar cola.
- `POST /queue/process` procesar cola.
- `GET /metrics` metricas.
- `GET /economics` analitica economica.
- `POST /delete-least-profitable` eliminacion inteligente.
- `GET /audit` auditoria AVL.
- `GET /compare` comparativa AVL/BST.
- `POST /stress-mode` activar/desactivar modo estres.
- `POST /critical-depth-limit` actualizar profundidad critica.
- `POST /rebalance-global` rebalanceo global.

### 7.2 Rutas de arbol/export

Base: `/trees`

- `POST /load-file`
- `GET /export/topology`
- `GET /export/insertion`
- `POST /export/topology-file`
- `POST /export/insertion-file`
- `GET /render-data/compare`
- `POST /undo`

### 7.3 Rutas de versiones

Base: `/versions`

- `POST /save`
- `GET /`
- `POST /restore/{name}`
- `DELETE /{name}`

## 8. Interfaz grafica

Pantallas principales:

- `Modos de Insercion`: selector JSON y profundidad critica.
- `Panel AVL de Vuelos`: gestion CRUD, cancelacion, versionado, undo, metricas y eliminacion inteligente.
- `Panel de Concurrencia`: cola y procesamiento.
- `Panel Modo Estres`: operaciones en estres + auditoria + rebalanceo.
- `Panel de Graficas`: comparacion AVL vs BST lado a lado.

## 9. Flujo tecnico de operaciones clave

### 9.1 Carga de archivo

1. UI selecciona ruta.
2. API `POST /trees/load-file`.
3. Loader reconstruye AVL/BST segun `tipo`.
4. UI consume `render-data/compare` para dibujar.

### 9.2 Eliminacion inteligente

1. API identifica candidato de menor rentabilidad.
2. Aplica snapshot undo.
3. Ejecuta `cancel_subtree` en AVL y BST.
4. Devuelve candidato seleccionado y metricas.

### 9.3 Profundidad critica

1. UI envia limite por `POST /flights/critical-depth-limit`.
2. AVL/BST recalculan metadatos.
3. `is_critical` y `final_price` se actualizan.
4. UI muestra nodos criticos con color diferencial.

## 10. Ejecucion local

### 10.1 Instalacion

```powershell
python -m pip install -r requirements.txt
```

### 10.2 Backend

```powershell
uvicorn app:app --reload
```

### 10.3 Frontend

```powershell
cd ui
flet run main.py -r
```

## 11. Pruebas

Se incluyeron pruebas unitarias orientadas a requisitos criticos:

- `tests/test_smart_delete.py`
- `tests/test_critical_depth_limit.py`
- `tests/test_undo_and_versions.py`

Ejecucion:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

## 12. Riesgos tecnicos y recomendaciones

- Estado global en memoria: no persiste reinicio de proceso.
- Ausencia de autenticacion/autorizacion en API.
- Recomendado migrar estado a almacenamiento persistente para produccion.
- Estandarizar logs y manejo de errores en UI para reemplazar `print` residuales.
