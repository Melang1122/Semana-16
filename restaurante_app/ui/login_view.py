import tkinter as tk
from pathlib import Path
from tkinter import ttk

from servicios.restaurante_servicio import RestauranteServicio


class LoginView(ttk.Frame):
    """Pantalla de acceso al sistema."""

    def __init__(
        self,
        master: tk.Misc,
        servicio: RestauranteServicio,
        on_login,
        assets_dir: str | Path,
    ) -> None:
        super().__init__(master, padding=30)
        self.servicio = servicio
        self.on_login = on_login
        self.assets_dir = Path(assets_dir)
        self.usuario_var = tk.StringVar()
        self.contrasena_var = tk.StringVar()
        self.mensaje_var = tk.StringVar()
        self.logo = None
        self._crear_componentes()

    def _cargar_logo(self) -> None:
        ruta = self.assets_dir / "logo" / "logo.png"
        try:
            self.logo = tk.PhotoImage(file=str(ruta))
        except tk.TclError:
            self.logo = None

    def _crear_componentes(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(7, weight=1)

        self._cargar_logo()
        if self.logo is not None:
            ttk.Label(self, image=self.logo).grid(
                row=1, column=0, columnspan=2, pady=(10, 6)
            )

        ttk.Label(
            self,
            text="RESTAURANTE APP",
            font=("Segoe UI", 22, "bold"),
        ).grid(row=2, column=0, columnspan=2, pady=(4, 6))

        ttk.Label(
            self,
            text="Semana 16 · Eventos y gestión de usuarios",
            font=("Segoe UI", 11),
        ).grid(row=3, column=0, columnspan=2, pady=(0, 22))

        ttk.Label(self, text="Usuario:").grid(
            row=4, column=0, sticky="e", padx=8, pady=8
        )
        entrada_usuario = ttk.Entry(self, textvariable=self.usuario_var, width=30)
        entrada_usuario.grid(row=4, column=1, sticky="w", padx=8, pady=8)

        ttk.Label(self, text="Contraseña:").grid(
            row=5, column=0, sticky="e", padx=8, pady=8
        )
        ttk.Entry(
            self,
            textvariable=self.contrasena_var,
            width=30,
            show="*",
        ).grid(row=5, column=1, sticky="w", padx=8, pady=8)

        ttk.Button(
            self,
            text="Ingresar",
            command=self._ingresar,
        ).grid(row=6, column=0, columnspan=2, pady=16)

        ttk.Label(
            self,
            textvariable=self.mensaje_var,
            foreground="red",
        ).grid(row=7, column=0, columnspan=2, sticky="n", pady=5)

        ttk.Label(
            self,
            text="Puede usar su identificación o correo como usuario.",
            font=("Segoe UI", 9),
        ).grid(row=8, column=0, columnspan=2, pady=(0, 10))

        entrada_usuario.focus()

    def _ingresar(self) -> None:
        usuario = self.usuario_var.get().strip()
        contrasena = self.contrasena_var.get().strip()

        if not usuario or not contrasena:
            self.mensaje_var.set("Complete usuario y contraseña.")
            return

        usuario_validado = self.servicio.validar_acceso(usuario, contrasena)
        if usuario_validado is None:
            self.mensaje_var.set("Usuario o contraseña incorrectos.")
            return

        self.mensaje_var.set("")
        self.on_login(usuario_validado)
