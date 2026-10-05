import json
from pathlib import Path
from typing import Any, Callable, TypeVar

from modelos.producto import Producto
from modelos.usuario import Usuario
from modelos.venta import Venta

T = TypeVar("T")


class ArchivoServicio:
    """Centraliza la lectura y escritura de los archivos JSON."""

    def __init__(self, directorio_datos: str | Path) -> None:
        self.directorio_datos = Path(directorio_datos)
        self.ruta_productos = self.directorio_datos / "productos.json"
        self.ruta_usuarios = self.directorio_datos / "usuarios.json"
        self.ruta_ventas = self.directorio_datos / "ventas.json"

    def _cargar(self, ruta: Path, constructor: Callable[[dict[str, Any]], T]) -> list[T]:
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                registros = json.load(archivo)
        except (FileNotFoundError, json.JSONDecodeError, PermissionError):
            return []

        if not isinstance(registros, list):
            return []

        objetos: list[T] = []
        for registro in registros:
            if not isinstance(registro, dict):
                continue
            try:
                objetos.append(constructor(registro))
            except (KeyError, ValueError, TypeError):
                continue
        return objetos

    def _guardar(self, ruta: Path, registros: list[dict[str, Any]]) -> None:
        self.directorio_datos.mkdir(parents=True, exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(registros, archivo, ensure_ascii=False, indent=4)

    def cargar_productos(self) -> list[Producto]:
        return self._cargar(
            self.ruta_productos,
            lambda r: Producto(r["codigo"], r["nombre"], r["categoria"], r["precio"], r["stock"]),
        )

    def cargar_usuarios(self) -> list[Usuario]:
        return self._cargar(
            self.ruta_usuarios,
            lambda r: Usuario(r["identificacion"], r["nombre"], r["correo"], r["contrasena"], r.get("rol", "Cliente")),
        )

    def cargar_ventas(self) -> list[Venta]:
        return self._cargar(
            self.ruta_ventas,
            lambda r: Venta(r["identificador"], r["usuario_id"], r["producto_codigo"], r["fecha"]),
        )

    def guardar_productos(self, productos: list[Producto]) -> None:
        self._guardar(self.ruta_productos, [producto.a_diccionario() for producto in productos])

    def guardar_ventas(self, ventas: list[Venta]) -> None:
        self._guardar(self.ruta_ventas, [venta.a_diccionario() for venta in ventas])

    def guardar_usuarios(self, usuarios: list[Usuario]) -> None:
        self._guardar(self.ruta_usuarios, [usuario.a_diccionario() for usuario in usuarios])
