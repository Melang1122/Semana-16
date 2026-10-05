class Venta:
    """Representa una venta sencilla entre un usuario, un producto y una fecha."""

    def __init__(self, identificador: str, usuario_id: str, producto_codigo: str, fecha: str) -> None:
        self.identificador = identificador
        self.usuario_id = usuario_id
        self.producto_codigo = producto_codigo
        self.fecha = fecha

    @staticmethod
    def _validar_texto(valor: str, campo: str) -> str:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"{campo} no puede estar vacío.")
        return valor.strip()

    @property
    def identificador(self) -> str:
        return self._identificador

    @identificador.setter
    def identificador(self, valor: str) -> None:
        self._identificador = self._validar_texto(valor, "El identificador")

    @property
    def usuario_id(self) -> str:
        return self._usuario_id

    @usuario_id.setter
    def usuario_id(self, valor: str) -> None:
        self._usuario_id = self._validar_texto(valor, "El usuario")

    @property
    def producto_codigo(self) -> str:
        return self._producto_codigo

    @producto_codigo.setter
    def producto_codigo(self, valor: str) -> None:
        self._producto_codigo = self._validar_texto(valor, "El producto")

    @property
    def fecha(self) -> str:
        return self._fecha

    @fecha.setter
    def fecha(self, valor: str) -> None:
        self._fecha = self._validar_texto(valor, "La fecha")

    def a_diccionario(self) -> dict[str, str]:
        return {
            "identificador": self.identificador,
            "usuario_id": self.usuario_id,
            "producto_codigo": self.producto_codigo,
            "fecha": self.fecha,
        }
