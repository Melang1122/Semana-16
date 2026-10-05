class Usuario:
    """Representa un usuario utilizado para el acceso simulado al sistema."""

    ROLES_PERMITIDOS = ("Administrador", "Empleado", "Cliente")

    def __init__(self, identificacion: str, nombre: str, correo: str, contrasena: str, rol: str = "Cliente") -> None:
        self.identificacion = identificacion
        self.nombre = nombre
        self.correo = correo
        self.contrasena = contrasena
        self.rol = rol

    @staticmethod
    def _validar_texto(valor: str, campo: str) -> str:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"{campo} no puede estar vacío.")
        return valor.strip()

    @property
    def identificacion(self) -> str:
        return self._identificacion

    @identificacion.setter
    def identificacion(self, valor: str) -> None:
        identificacion = self._validar_texto(valor, "La identificación")
        if not identificacion.isdigit():
            raise ValueError("La identificación debe contener únicamente números.")
        self._identificacion = identificacion

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        nombre = self._validar_texto(valor, "El nombre")
        if any(caracter.isdigit() for caracter in nombre):
            raise ValueError("El nombre no puede contener números.")
        self._nombre = nombre

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        correo = self._validar_texto(valor, "El correo").lower()
        if "@" not in correo or "." not in correo.split("@")[-1]:
            raise ValueError("Ingrese un correo electrónico válido.")
        self._correo = correo

    @property
    def contrasena(self) -> str:
        return self._contrasena

    @contrasena.setter
    def contrasena(self, valor: str) -> None:
        self._contrasena = self._validar_texto(valor, "La contraseña")

    @property
    def rol(self) -> str:
        return self._rol

    @rol.setter
    def rol(self, valor: str) -> None:
        rol = self._validar_texto(valor, "El rol")
        if rol not in self.ROLES_PERMITIDOS:
            raise ValueError("Seleccione un rol válido.")
        self._rol = rol

    def a_diccionario(self) -> dict[str, str]:
        return {
            "identificacion": self.identificacion,
            "nombre": self.nombre,
            "correo": self.correo,
            "contrasena": self.contrasena,
            "rol": self.rol,
        }

    def mostrar_informacion(self) -> str:
        return (
            f"Identificación: {self.identificacion} | "
            f"Nombre: {self.nombre} | Correo: {self.correo}"
        )

    def __str__(self) -> str:
        return self.mostrar_informacion()
