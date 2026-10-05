from datetime import date

from modelos.producto import Producto
from modelos.usuario import Usuario
from modelos.venta import Venta
from servicios.archivo_servicio import ArchivoServicio


class RestauranteServicio:
    """Concentra las reglas y operaciones de negocio del restaurante."""

    def __init__(
        self,
        productos: list[Producto],
        usuarios: list[Usuario],
        ventas: list[Venta] | None = None,
        archivos: ArchivoServicio | None = None,
    ) -> None:
        self._productos = list(productos)
        self._usuarios = list(usuarios)
        self._ventas = list(ventas or [])
        self._archivos = archivos

    def validar_acceso(self, usuario: str, contrasena: str) -> Usuario | None:
        usuario = usuario.strip().lower()
        contrasena = contrasena.strip()
        if not usuario or not contrasena:
            return None
        for registrado in self._usuarios:
            coincide_usuario = (
                registrado.identificacion == usuario
                or registrado.correo.lower() == usuario
            )
            if coincide_usuario and registrado.contrasena == contrasena:
                return registrado
        return None

    def listar_productos(self) -> list[Producto]:
        return self._productos.copy()

    def listar_usuarios(self) -> list[Usuario]:
        return self._usuarios.copy()

    def listar_ventas(self) -> list[Venta]:
        return self._ventas.copy()

    def cantidad_productos(self) -> int:
        return len(self._productos)

    def cantidad_usuarios(self) -> int:
        return len(self._usuarios)

    def cantidad_ventas(self) -> int:
        return len(self._ventas)

    def buscar_producto(self, codigo: str) -> Producto | None:
        codigo = str(codigo).strip()
        for producto in self._productos:
            if producto.codigo == codigo:
                return producto
        return None

    def buscar_usuario(self, identificacion: str) -> Usuario | None:
        identificacion = str(identificacion).strip()
        for usuario in self._usuarios:
            if usuario.identificacion == identificacion:
                return usuario
        return None

    def registrar_producto(self, codigo: str, nombre: str, categoria: str, precio: float, stock: int) -> Producto:
        if self.buscar_producto(codigo) is not None:
            raise ValueError("Ya existe un producto con ese código.")
        producto = Producto(codigo, nombre, categoria, precio, stock)
        self._productos.append(producto)
        self._guardar_productos()
        return producto

    def actualizar_producto(self, codigo: str, nombre: str, categoria: str, precio: float, stock: int) -> Producto:
        producto = self.buscar_producto(codigo)
        if producto is None:
            raise ValueError("No existe un producto con ese código.")
        producto.actualizar(nombre, categoria, precio, stock)
        self._guardar_productos()
        return producto

    def eliminar_producto(self, codigo: str) -> None:
        producto = self.buscar_producto(codigo)
        if producto is None:
            raise ValueError("No existe un producto con ese código.")
        self._productos.remove(producto)
        self._guardar_productos()

    def _generar_identificador_venta(self) -> str:
        numeros = []
        for venta in self._ventas:
            if venta.identificador.startswith("V") and venta.identificador[1:].isdigit():
                numeros.append(int(venta.identificador[1:]))
        siguiente = max(numeros, default=0) + 1
        return f"V{siguiente:03d}"

    def registrar_venta(self, usuario_id: str, producto_codigo: str) -> Venta:
        """Valida y registra una venta. La UI solo coordina el evento."""
        usuario_id = str(usuario_id).strip()
        producto_codigo = str(producto_codigo).strip()

        if not usuario_id:
            raise ValueError("Debe seleccionar un usuario.")
        if not producto_codigo:
            raise ValueError("Debe seleccionar un producto.")
        if self.buscar_usuario(usuario_id) is None:
            raise ValueError("El usuario seleccionado no existe.")
        producto = self.buscar_producto(producto_codigo)
        if producto is None:
            raise ValueError("El producto seleccionado no existe.")
        if producto.stock <= 0:
            raise ValueError("El producto seleccionado no tiene stock disponible.")

        nueva_venta = Venta(
            self._generar_identificador_venta(),
            usuario_id,
            producto_codigo,
            date.today().isoformat(),
        )
        self._ventas.append(nueva_venta)
        self._guardar_ventas()
        return nueva_venta

    def _guardar_productos(self) -> None:
        if self._archivos is not None:
            self._archivos.guardar_productos(self._productos)

    def _guardar_ventas(self) -> None:
        if self._archivos is not None:
            self._archivos.guardar_ventas(self._ventas)

    def _exigir_administrador(self, actor_id: str) -> Usuario:
        actor = self.buscar_usuario(actor_id)
        if actor is None or actor.rol != "Administrador":
            raise ValueError("Solo el administrador puede gestionar usuarios.")
        return actor

    def _validar_correo_unico(self, correo: str, excluir_id: str | None = None) -> None:
        if any(u.correo == correo and u.identificacion != excluir_id for u in self._usuarios):
            raise ValueError("Ya existe un usuario con ese correo.")

    def _guardar_usuarios(self, usuarios: list[Usuario]) -> None:
        if self._archivos is not None:
            self._archivos.guardar_usuarios(usuarios)

    def registrar_usuario(self, identificacion: str, nombre: str, correo: str,
                          contrasena: str, rol: str, *, actor_id: str) -> Usuario:
        self._exigir_administrador(actor_id)
        nuevo = Usuario(identificacion, nombre, correo, contrasena, rol)
        if nuevo.rol == "Administrador":
            raise ValueError("Desde esta sección solo se registran empleados y clientes.")
        if self.buscar_usuario(nuevo.identificacion) is not None:
            raise ValueError("Ya existe un usuario con esa identificación.")
        if any(v.usuario_id == nuevo.identificacion for v in self._ventas):
            raise ValueError("Esa identificación pertenece al historial de ventas de un usuario eliminado.")
        self._validar_correo_unico(nuevo.correo)
        usuarios = [*self._usuarios, nuevo]
        self._guardar_usuarios(usuarios)
        self._usuarios = usuarios
        return nuevo

    def actualizar_usuario(self, identificacion: str, nombre: str, correo: str,
                           contrasena: str, rol: str, *, actor_id: str) -> Usuario:
        self._exigir_administrador(actor_id)
        actual = self.buscar_usuario(identificacion)
        if actual is None:
            raise ValueError("El usuario seleccionado ya no existe.")
        # Una contraseña vacía conserva la actual, sin exponerla en la tabla o formulario.
        candidato = Usuario(actual.identificacion, nombre, correo,
                            contrasena if contrasena.strip() else actual.contrasena, rol)
        if actual.rol == "Administrador" and candidato.rol != "Administrador":
            raise ValueError("No puede cambiar el rol de la cuenta administradora.")
        if actual.rol != "Administrador" and candidato.rol == "Administrador":
            raise ValueError("Desde esta sección no se asigna el rol Administrador.")
        self._validar_correo_unico(candidato.correo, actual.identificacion)
        usuarios = [candidato if u.identificacion == actual.identificacion else u for u in self._usuarios]
        self._guardar_usuarios(usuarios)
        # Conserva el objeto que usa la sesión y actualiza solo después de guardar.
        actual.nombre, actual.correo = candidato.nombre, candidato.correo
        actual.contrasena, actual.rol = candidato.contrasena, candidato.rol
        return actual

    def eliminar_usuario(self, identificacion: str, *, actor_id: str) -> None:
        self._exigir_administrador(actor_id)
        actual = self.buscar_usuario(identificacion)
        if actual is None:
            raise ValueError("El usuario seleccionado ya no existe.")
        if actual.identificacion == actor_id or actual.rol == "Administrador":
            raise ValueError("No puede eliminar la cuenta administradora.")
        usuarios = [u for u in self._usuarios if u.identificacion != actual.identificacion]
        self._guardar_usuarios(usuarios)
        self._usuarios = usuarios
