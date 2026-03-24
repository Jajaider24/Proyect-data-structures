class Pila:
    def __init__(self):
        self._datos = []

    # Metodo que me sirve para agregar (apilar) un dato en la pila
    # dato: informacion a agregar
    def apilar(self, dato):
        self._datos.append(dato)

    def desapilar(self):
        if self.estaVacia():
            raise Exception("La pila esta vacia")
        else:
            return self._datos.pop()

    # Metodo que valida si la pila esta vacia o no
    # return: booleano => true: si esta vacia, false: si tiene elementos
    def estaVacia(self):
        return len(self._datos) == 0

    def obtenerElemento(self):
        if self.estaVacia():
            raise Exception("La pila esta vacia")
        else:
            return self._datos[-1]
