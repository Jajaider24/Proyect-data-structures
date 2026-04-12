class Pila:
    def __init__(self):
        self._datos = []

    # Method I use to add (push) data to the stack
    # data: information to be added
    def apilar(self, dato):
        self._datos.append(dato)

    def desapilar(self):
        if self.estaVacia():
            raise Exception("La pila esta vacia")
        else:
            return self._datos.pop()

    # Method that validates if the stack is empty or not
    # return: boolean => true: if it is empty, false: if it has elements
    def estaVacia(self):
        return len(self._datos) == 0

    def obtenerElemento(self):
        if self.estaVacia():
            raise Exception("La pila esta vacia")
        else:
            return self._datos[-1]
