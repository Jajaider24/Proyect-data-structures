# Manual de Usuario

## 1. Introduccion

SkyBalance AVL es una aplicacion para gestionar vuelos usando un arbol AVL como estructura principal y un BST como estructura de comparacion.

El sistema permite:

- Cargar vuelos desde JSON.
- Crear, editar, eliminar o cancelar vuelos.
- Simular procesamiento por cola.
- Activar modo estres y ejecutar rebalanceo global.
- Consultar metricas, auditoria y comparativa AVL vs BST.
- Guardar versiones y deshacer acciones.

## 2. Requisitos de ejecucion

- Python 3.13 o compatible.
- Dependencias instaladas desde `requirements.txt`.

## 3. Encendido del sistema

### 3.1 Backend API

1. Abrir terminal en la raiz del proyecto.
2. Activar entorno virtual.
3. Ejecutar:

```powershell
uvicorn app:app --reload
```

4. Validar API en:

- `http://127.0.0.1:8000/docs`

### 3.2 Interfaz grafica (Flet)

1. Abrir nueva terminal.
2. Ir a carpeta `ui`.
3. Ejecutar:

```powershell
flet run main.py -r
```

## 4. Flujo recomendado de uso

1. Ingresar a `Modos de Insercion`.
2. (Opcional) definir `Profundidad Critica` y aplicar.
3. Seleccionar archivo JSON para cargar el arbol.
4. Ir a `Panel AVL de Vuelos` para gestion operacional.
5. Usar `Panel de Concurrencia` para cola de inserciones.
6. Usar `Panel Modo Estres` para pruebas sin balanceo inmediato.
7. Revisar `Panel de Graficas` para comparar AVL vs BST.

## 5. Modulo Modos de Insercion

Permite cargar el arbol desde archivo JSON seleccionado por el usuario.

Funciones disponibles:

- `Arbol a Insertar`: abre selector de archivos.
- `Profundidad Critica`: campo para definir limite de criticidad.
- `Aplicar Profundidad Critica`: recalcula criticidad y precios.

Notas:

- Si la profundidad critica queda vacia, se desactiva el limite.
- El archivo puede estar en modo `INSERCION` o `TOPOLOGIA`.

## 6. Panel AVL de Vuelos

Funciones principales:

- Crear vuelo.
- Modificar vuelo.
- Eliminar o cancelar vuelo.
- Guardar arbol y version.
- Eliminacion inteligente.
- Retroceso.
- Restaurar version.
- Ver metricas.

### 6.1 Eliminar vs Cancelar

- `Eliminar`: borra solo el nodo objetivo.
- `Cancelar`: borra el nodo y toda su subrama.

### 6.2 Eliminacion Inteligente

Selecciona automaticamente el vuelo de menor rentabilidad y aplica cancelacion de subrama.

Criterios de desempate:

1. Menor rentabilidad.
2. Mayor profundidad.
3. Mayor codigo normalizado.

## 7. Panel de Concurrencia

Permite simular inserciones diferidas mediante cola.

Flujo:

1. Registrar datos del vuelo.
2. Pulsar `Agregar a Cola`.
3. Pulsar `Procesar` para ejecutar inserciones.

## 8. Panel Modo Estres

Permite operar sin rebalanceo automatico inmediato.

Funciones:

- Crear, modificar, eliminar/cancelar vuelos.
- Rebalanceo global.
- Auditoria AVL.

Uso recomendado:

1. Operar en modo estres.
2. Revisar deformacion visual del arbol.
3. Ejecutar `Rebalanceo Global`.
4. Verificar con `Auditoria AVL`.

## 9. Panel de Graficas

Muestra comparacion estructural AVL vs BST en paralelo.

Incluye:

- Vista grafica lado a lado.
- Resumen de raiz, altura y hojas por arbol.
- Boton de actualizacion para refrescar datos.

## 10. Versionado y retroceso

### 10.1 Guardar version

Desde panel AVL, usar `Guardar Arbol` y asignar nombre.

### 10.2 Restaurar version

Desde panel AVL, usar `Restaurar Version` y elegir una version guardada.

### 10.3 Retroceso

Desde panel AVL, `Retroceso` revierte la accion mas reciente con snapshot.

## 11. Mensajes y errores comunes

- `No hay vuelos para eliminar`: el arbol esta vacio.
- `No hay acciones para deshacer`: historial undo vacio.
- `La version solicitada no existe`: nombre de version invalido.
- Errores de conexion: validar que API este activa en `127.0.0.1:8000`.

## 12. Buenas practicas

- Cargar un JSON valido antes de operar.
- Guardar versiones antes de cambios grandes.
- Usar modo estres solo para simulaciones controladas.
- Ejecutar auditoria despues de rebalanceo global.
