class Producto:
    """Representa un producto y mantiene sus propias validaciones."""

    def __init__(self, codigo: str, nombre: str, categoria: str, precio: float, stock: int) -> None:
        self.codigo = codigo
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.stock = stock

    @staticmethod
    def _validar_texto(valor: str, campo: str) -> str:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"{campo} no puede estar vacío y debe ser texto.")
        return valor.strip()

    @property
    def codigo(self) -> str:
        return self._codigo

    @codigo.setter
    def codigo(self, valor: str) -> None:
        self._codigo = self._validar_texto(valor, "El código")

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = self._validar_texto(valor, "El nombre")

    @property
    def categoria(self) -> str:
        return self._categoria

    @categoria.setter
    def categoria(self, valor: str) -> None:
        self._categoria = self._validar_texto(valor, "La categoría")

    @property
    def precio(self) -> float:
        return self._precio

    @precio.setter
    def precio(self, valor: float) -> None:
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor < 0:
            raise ValueError("El precio debe ser numérico e igual o mayor que 0.")
        self._precio = float(valor)

    @property
    def stock(self) -> int:
        return self._stock

    @stock.setter
    def stock(self, valor: int) -> None:
        if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
            raise ValueError("El stock debe ser un entero igual o mayor que 0.")
        self._stock = valor

    def actualizar(self, nombre: str, categoria: str, precio: float, stock: int) -> None:
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.stock = stock

    def vender(self, cantidad: int) -> None:
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("La cantidad debe ser un entero mayor que 0.")
        if cantidad > self.stock:
            raise ValueError("No existe stock suficiente.")
        self.stock -= cantidad

    def a_diccionario(self) -> dict[str, str | float | int]:
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "precio": self.precio,
            "stock": self.stock,
        }

    def mostrar_informacion(self) -> str:
        return (
            f"Código: {self.codigo} | Nombre: {self.nombre} | "
            f"Categoría: {self.categoria} | Precio: ${self.precio:.2f} | Stock: {self.stock}"
        )

    def __str__(self) -> str:
        return self.mostrar_informacion()
