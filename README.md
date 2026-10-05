# Restaurante App — Semana 16

Aplicación de Programación Orientada a Objetos en Python y Tkinter. Esta versión continúa el proyecto de la Semana 15: conserva el inicio de sesión, navegación, CRUD de productos, registro de ventas, persistencia JSON, logo e íconos. La ampliación se concentra en la gestión de usuarios mediante eventos.

## Ejecución

Requiere Python 3.10 o posterior con Tkinter. No utiliza librerías externas. Para comprobar Tkinter:

```bash
python -m tkinter
```

Desde la carpeta que contiene este README:

```bash
cd restaurante_app
python main.py
```

En Windows también puede utilizarse `py main.py`. El aplicativo localiza datos y recursos mediante rutas relativas a `main.py`, independientemente del directorio de trabajo.

### Cuenta administradora existente

- Identificación: `0922248737`.
- Contraseña: `1234`.
- También se conserva el acceso por el correo existente en `usuarios.json`.
- Se añadió el rol `Administrador` a esta cuenta, conservando sus demás datos.

## Estructura

```text
README.md
restaurante_app/
    main.py
    README.md
    datos/
        productos.json
        usuarios.json
        ventas.json
    modelos/
        __init__.py
        usuario.py
        producto.py
        venta.py
    servicios/
        __init__.py
        archivo_servicio.py
        restaurante_servicio.py
    ui/
        __init__.py
        login_view.py
        main_view.py
    assets/
        icons/
        logo/
tests/
    test_usuarios.py
```

## Gestión de usuarios y roles

Solo el Administrador ve la opción Usuarios. La vista también comprueba el rol al abrirse y RestauranteServicio valida al actor que solicita cada operación administrativa. Empleados y Clientes conservan el acceso a las otras secciones previamente existentes, pero no administran usuarios. No se añade una matriz de permisos avanzada.

El administrador puede registrar Empleados y Clientes, consultar sus datos, seleccionarlos, actualizarlos y eliminarlos con confirmación. Se conservan identificación y correo como formas de ingreso. La tabla presenta identificación, nombre, correo/usuario y rol; nunca contiene contraseñas.

La identificación queda de solo lectura al seleccionar un usuario. Una contraseña vacía durante la actualización conserva la anterior. Para registrar, la contraseña es obligatoria. No se permite crear o promover cuentas Administrador desde este formulario, eliminar la cuenta administradora o cambiar su rol. La cuenta administradora puede actualizar sus datos manteniendo su rol.

Se validan datos obligatorios, identificación numérica, nombre sin números, formato básico del correo, rol permitido, identificación única y correo único sin distinguir mayúsculas. Las validaciones de los modelos existentes se reutilizan desde el servicio.

## Eventos implementados

| Interacción | Asociación | Callback y respuesta |
|---|---|---|
| Selección de fila | `tabla_usuarios.bind("<<TreeviewSelect>>", ...)` | `_seleccionar_usuario(event)` obtiene la identificación de la fila y llama a `buscar_usuario()` del servicio para cargar el formulario. |
| Enter en los campos o selector de rol | `widget.bind("<Return>", ...)` | `_usuario_enter(event)` reutiliza `_registrar_usuario()`. |
| Escape en formulario, acciones o tabla | `widget.bind("<Escape>", ...)` | `_usuario_escape(event)` limpia campos y selección, restablece Cliente y devuelve el foco a Identificación. |
| Cambio de rol | `combo.bind("<<ComboboxSelected>>", ...)` | `_seleccionar_rol(event)` muestra el rol seleccionado. |
| Botones Registrar, Actualizar, Eliminar y Limpiar | `command=callback` mediante `_boton()` | Ejecutan las operaciones correspondientes. |

`command=` representa la acción principal del botón y no entrega automáticamente un objeto event. `bind()` asocia un evento concreto al componente y su callback recibe event. Los atajos son locales a Usuarios; no se usa `bind_all()` para afectar otras secciones. Enter y Escape devuelven `"break"` para evitar propagar la misma interacción.

Si hay un usuario seleccionado, Enter no crea una copia: solicita usar Actualizar o Limpiar. Para registrar otra persona, primero se limpia el formulario.

## Flujo y responsabilidades

1. El usuario interactúa con un componente.
2. Tkinter detecta el evento y ejecuta el callback asociado.
3. La interfaz obtiene los campos o la identificación seleccionada.
4. RestauranteServicio comprueba permisos y reglas y solicita la persistencia.
5. ArchivoServicio escribe usuarios.json.
6. La interfaz refresca la tabla y presenta el resultado.

La interfaz no lee ni escribe JSON. Usuario representa datos y valida propiedades. RestauranteServicio administra operaciones. ArchivoServicio concentra lectura/escritura. La tabla es una representación, no la fuente real de los objetos.

## Persistencia y continuidad

Se conserva el producto original y ventas.json tal como se recibió. El ZIP original no contenía ventas registradas; no se añaden ventas ficticias. Los nuevos usuarios se escriben en usuarios.json con su rol. Al reiniciar, se recuperan como objetos Usuario. Si un registro antiguo no incluye rol, se interpreta como Cliente; la cuenta administradora incluida ya tiene su rol explícito.

Eliminar un usuario no borra las ventas históricas. La tabla de ventas conserva la identificación si el usuario ya no existe. No se permite reutilizar una identificación que aún figure en ese historial para evitar atribuir ventas antiguas a otra persona.

Los cambios de usuarios se escriben antes de modificar la colección en memoria. Si la escritura falla, se muestra el error y el servicio conserva su estado anterior.

## Pruebas automatizadas

Desde la carpeta que contiene este README:

```bash
python -m unittest discover -s tests -v
```

Se ejecutaron 13 pruebas y todas pasaron: registro/recarga de roles, actualización, contraseña conservada y cambiada, eliminación/recarga, duplicados, datos inválidos, restricciones del Administrador, permisos del servicio, fallo de escritura, conservación del historial, operaciones de productos/ventas y reutilización de callbacks de teclado. Las pruebas utilizan carpetas temporales y no alteran los JSON incluidos.

También se comprobó la sintaxis de los archivos Python. La ventana gráfica y la entrega en GitHub deben verificarse en el equipo del estudiante; no se afirma que se haya probado visualmente en Windows.

## Comprobación de interfaz antes de entregar

1. Abrir main.py e ingresar con la cuenta administradora.
2. Revisar Inicio, Productos y Ventas.
3. Abrir Usuarios y registrar un Cliente con identificación numérica y correo no repetidos.
4. Comprobar que aparece en la tabla, con su rol y sin contraseña visible.
5. Seleccionar la fila y revisar la carga automática del formulario.
6. Modificar su nombre y pulsar Actualizar.
7. Registrar un Empleado pulsando Enter desde el formulario, con ninguna fila seleccionada.
8. Cambiar el rol en el Combobox y comprobar el texto de respuesta.
9. Seleccionar un usuario y pulsar Escape: campos y selección deben limpiarse.
10. Cancelar primero una eliminación y después confirmar la eliminación de un usuario de prueba.
11. Intentar eliminar la cuenta administradora: el servicio debe impedirlo.
12. Cerrar la sesión, ingresar como Empleado o Cliente y comprobar que Usuarios no aparece.
13. Reiniciar la aplicación y comprobar la recuperación de los cambios desde usuarios.json.
14. Volver a ingresar como Administrador y comprobar que la navegación y la grabación de ventas siguen disponibles.

## Entrega en GitHub

Extraer el ZIP y subir el contenido: README.md, restaurante_app completo y tests. No entregar únicamente el ZIP como archivo dentro de un repositorio vacío. El repositorio debe ser público e incluir los archivos .py, JSON y assets. Copiar la URL del repositorio y comprobar que abre sin iniciar sesión. Esa URL es la entrega solicitada por el docente. Esta versión no ha sido publicada automáticamente.

## Referencias de estudio

- Guía Semana 16 y consignas del docente proporcionadas para esta tarea.
- Ejemplo docente: https://github.com/kevin10lascano-sketch/Clase-Semana-16-POO.git
- Explorador complementario: https://github.com/kevin10lascano-sketch/Clase-Semana-16.1-POO.git
- Documentación Tkinter: https://docs.python.org/es/3.14/library/tkinter.html
- Documentación ttk: https://docs.python.org/es/3.14/library/tkinter.ttk.html
- Recursos de video proporcionados: https://www.youtube.com/watch?v=url8wUC7TEM ; https://www.youtube.com/watch?v=bjdOvzbrL1Y ; https://www.youtube.com/watch?v=XNa1vKz-P0Q

La implementación adapta la referencia al restaurante y conserva sus modelos, servicios, nombres y recursos. El Explorador y los videos son recursos de estudio; no se exige incorporar todos sus eventos. No se añaden bases de datos, Supabase, bloqueo de cuentas, recuperación de contraseña o permisos avanzados. El archivo __init__.py de Tkinter suministrado como consulta no se copia dentro del proyecto.
