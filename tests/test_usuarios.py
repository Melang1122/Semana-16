"""Pruebas con JSON temporales. No modifican los datos de la aplicación."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'restaurante_app'))
from modelos.usuario import Usuario
from modelos.producto import Producto
from servicios.archivo_servicio import ArchivoServicio
from servicios.restaurante_servicio import RestauranteServicio
from ui.main_view import MainView

class UsuariosTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.arch = ArchivoServicio(self.temp.name)
        self.admin = Usuario('100', 'Administradora', 'admin@example.com', 'clave', 'Administrador')
        self.producto = Producto('P001', 'Arroz', 'Comida', 3.5, 10)
        self.arch.guardar_usuarios([self.admin])
        self.arch.guardar_productos([self.producto])
        self.s = RestauranteServicio([self.producto], [self.admin], archivos=self.arch)

    def nuevo(self, identificacion='200', correo='cliente@example.com', rol='Cliente'):
        return self.s.registrar_usuario(identificacion, 'Persona Ejemplo', correo, 'clave', rol, actor_id='100')

    def test_registrar_roles_y_recargar(self):
        self.nuevo()
        self.nuevo('300', 'empleado@example.com', 'Empleado')
        roles = {u.rol for u in self.arch.cargar_usuarios()}
        self.assertEqual(roles, {'Administrador', 'Empleado', 'Cliente'})

    def test_actualizar_y_conservar_password(self):
        u = self.nuevo()
        self.s.actualizar_usuario('200', 'Nombre Nuevo', 'nuevo@example.com', '', 'Empleado', actor_id='100')
        self.assertEqual(u.contrasena, 'clave')
        recuperado = next(x for x in self.arch.cargar_usuarios() if x.identificacion=='200')
        self.assertEqual((recuperado.nombre, recuperado.rol), ('Nombre Nuevo', 'Empleado'))
        self.assertIs(self.s.validar_acceso('nuevo@example.com', 'clave'), u)

    def test_cambiar_password(self):
        self.nuevo()
        self.s.actualizar_usuario('200', 'Persona Ejemplo', 'cliente@example.com', 'nueva', 'Cliente', actor_id='100')
        self.assertIsNotNone(self.s.validar_acceso('200', 'nueva'))
        self.assertIsNone(self.s.validar_acceso('200', 'clave'))

    def test_eliminar_y_recargar(self):
        self.nuevo()
        self.s.eliminar_usuario('200', actor_id='100')
        self.assertIsNone(self.s.buscar_usuario('200'))
        self.assertEqual(len(self.arch.cargar_usuarios()), 1)

    def test_duplicados(self):
        self.nuevo()
        for identificacion, correo in [('200','otro@example.com'), ('300','CLIENTE@example.com')]:
            with self.assertRaises(ValueError):self.nuevo(identificacion,correo)
        self.assertEqual(len(self.s.listar_usuarios()), 2)

    def test_validaciones_sin_modificar_datos(self):
        for args in [('ABC','Nombre','a@example.com','clave','Cliente'),
                     ('200','Nombre 2','a@example.com','clave','Cliente'),
                     ('200','Nombre','incorrecto','clave','Cliente'),
                     ('200','Nombre','a@example.com','','Cliente'),
                     ('200','Nombre','a@example.com','clave','Otro')]:
            with self.assertRaises(ValueError):self.s.registrar_usuario(*args,actor_id='100')
        self.assertEqual(len(self.arch.cargar_usuarios()),1)

    def test_no_crear_ni_promover_admin(self):
        with self.assertRaises(ValueError):self.nuevo(rol='Administrador')
        self.nuevo()
        with self.assertRaises(ValueError):
            self.s.actualizar_usuario('200','Persona Ejemplo','cliente@example.com','clave','Administrador',actor_id='100')

    def test_proteger_administrador(self):
        with self.assertRaises(ValueError):self.s.eliminar_usuario('100',actor_id='100')
        with self.assertRaises(ValueError):
            self.s.actualizar_usuario('100','Administradora','admin@example.com','clave','Cliente',actor_id='100')
        self.assertEqual(self.admin.rol,'Administrador')

    def test_permisos_en_servicio(self):
        for rol in ('Cliente','Empleado'):
            u=self.nuevo('200' if rol=='Cliente' else '300', rol.lower()+'@example.com',rol)
            with self.assertRaises(ValueError):self.s.registrar_usuario('400','Nombre','otra@example.com','clave','Cliente',actor_id=u.identificacion)
            with self.assertRaises(ValueError):self.s.actualizar_usuario(u.identificacion,'Nombre',u.correo,'clave',rol,actor_id=u.identificacion)
            with self.assertRaises(ValueError):self.s.eliminar_usuario(u.identificacion,actor_id=u.identificacion)

    def test_fallo_guardado_no_altera_memoria(self):
        with patch.object(self.arch,'guardar_usuarios',side_effect=OSError('Sin permiso')):
            with self.assertRaises(OSError):self.nuevo()
        self.assertEqual(len(self.s.listar_usuarios()),1)
        u=self.nuevo()
        with patch.object(self.arch,'guardar_usuarios',side_effect=OSError('Sin permiso')):
            with self.assertRaises(OSError):self.s.actualizar_usuario('200','Nombre Nuevo',u.correo,'clave','Cliente',actor_id='100')
            with self.assertRaises(OSError):self.s.eliminar_usuario('200',actor_id='100')
        self.assertEqual(u.nombre,'Persona Ejemplo')
        self.assertIsNotNone(self.s.buscar_usuario('200'))

    def test_historial_ventas_se_conserva(self):
        self.nuevo()
        venta=self.s.registrar_venta('200','P001')
        self.s.eliminar_usuario('200',actor_id='100')
        self.assertEqual(self.arch.cargar_ventas()[0].identificador,venta.identificador)
        with self.assertRaises(ValueError):self.nuevo()

    def test_productos_y_ventas(self):
        self.s.registrar_producto('P002','Sopa','Comida',2.5,5)
        self.s.actualizar_producto('P002','Sopa Especial','Comida',3,4)
        self.assertEqual(self.arch.cargar_productos()[1].nombre,'Sopa Especial')
        venta=self.s.registrar_venta('100','P001')
        self.assertEqual(self.arch.cargar_ventas()[0].identificador,venta.identificador)
        self.s.eliminar_producto('P002')
        self.assertIsNone(self.s.buscar_producto('P002'))

    def test_callbacks_teclado_reutilizan_operaciones(self):
        from unittest.mock import Mock
        vista=Mock()
        self.assertEqual(MainView._usuario_enter(vista,None),'break')
        vista._registrar_usuario.assert_called_once_with()
        self.assertEqual(MainView._usuario_escape(vista,None),'break')
        vista._limpiar_usuario.assert_called_once_with()

if __name__ == '__main__':unittest.main()
