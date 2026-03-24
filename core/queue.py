from collections import deque
from typing import Any


class Cola:
    def __init__(self):
        self._datos = deque()

    # Metodo para agregar (encolar) un dato al final de la cola
    # dato: informacion a agregar
    def encolar(self, dato: Any):
        self._datos.append(dato)

    def desencolar(self):
        if self.estaVacia():
            raise Exception("La cola esta vacia")
        else:
            return self._datos.popleft()

    # Metodo que valida si la cola esta vacia o no
    # return: booleano => true: si esta vacia, false: si tiene elementos
    def estaVacia(self):
        return len(self._datos) == 0

    # Retorna el primer elemento que saldria de la cola (frente)
    def obtenerElemento(self):
        if self.estaVacia():
            raise Exception("La cola esta vacia")
        else:
            return self._datos[0]

    def __len__(self) -> int:
        return len(self._datos)

    def __iter__(self):
        return iter(self._datos)

    def limpiar(self):
        self._datos.clear()
