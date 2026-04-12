from collections import deque
from typing import Any


class Cola:
    def __init__(self):
        self._datos = deque()

    # Method for appending data to the end of the queue
    # data: information to be appended
    def encolar(self, dato: Any):
        self._datos.append(dato)

    def desencolar(self):
        if self.estaVacia():
            raise Exception("La cola esta vacia")
        else:
            return self._datos.popleft()

    # Method that validates if the queue is empty or not
    # return: boolean => true: if it is empty, false: if it has elements
    def estaVacia(self):
        return len(self._datos) == 0

    # Method that returns the first element that would be dequeued (front)
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
