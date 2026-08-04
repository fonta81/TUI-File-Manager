from pathlib import Path
from typing import ClassVar
from datetime import datetime

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Static

class VentanaConfirmacion(ModalScreen[bool]):  # Retorna True o False
    def __init__(self, mensaje: str, **kwargs):
        super().__init__(**kwargs)
        self.mensaje = mensaje  # guardamos el mensaje a mostrar

    def compose(self) -> ComposeResult:  # mostramos el mensaje:
        texto_instrucciones = (
            f"{self.mensaje}\n\n"
            "[dim]Presiona [b]S[/b] para confirmar, [b]N[/b] o [b]Esc[/b] para cancelar.[/]"
        )
        yield Grid(
            Label("CONFIRMACIÓN", id="modal_title"),
            # antes habia un Input aqui que robaba el foco y capturaba teclas
            # ahora solo mostramos el texto y esperamos teclas directas
            Static(texto_instrucciones, id="modal_content"),
            id="modal_dialog",
        )

    def on_key(self, event) -> None:  # Permite responder con una sola tecla sin Enter
        key = event.key.lower()  # convertimos a minusculas para comparar facil
        if key == "s":  # Si presiona S -> confirma
            self.dismiss(True)  # cerramos modal devolviendo True
        elif key in ("n", "escape"):  # Si presiona N o Esc -> cancela
            self.dismiss(False)  # cerramos modal devolviendo False

    # ya no hay on_input_submitted porque quitamos el Input widget


class VentanaAyuda(ModalScreen):  # ventana help
    # Atajos para cerrar la ayuda rápidamente con Esc, ? o q
    BINDINGS: ClassVar[list[Binding]] = [
        Binding("escape,?,q", "dismiss", "Cerrar Ayuda")
    ]

    def compose(self) -> ComposeResult:  # ayuda:
        texto_ayuda = (
            "[bold]Guía de Atajos de Teclado[/]\n\n"
            "[substantive]Navegación:[/]\n"
            "  [b]k[/] o [b]↑[/]     - Subir en el árbol\n"
            "  [b]j[/] o [b]↓[/]     - Bajar en el árbol\n\n"
            "[substantive]Acciones:[/]\n\n"
            "  [b]n[/]         - Crear una nueva carpeta\n"
            "  [b]N[/]         - Crear un archivo\n"
            "  [b]r[/]         - Renombrar archivo o carpeta\n"
            "  [b]m[/]         - Mover archivo o carpeta\n"
            "  [b]c[/]         - Copiar elemento seleccionado\n"
            "  [b]v[/]         - Ver contenido de un archivo de texto\n"
            "  [b]e[/]         - Editar archivo con editor externo ($EDITOR)\n"
            "  [b]o[/]         - Abrir archivo con app predeterminada (xdg-open)\n"
            "  [b]p[/]         - Ver propiedades del archivo (tamaño, permisos)\n"
            "  [b]z[/]         - Comprimir a .zip\n"
            "  [b]Z[/]         - Descomprimir .zip\n"
            "  [b]y[/]         - Copiar ruta al portapapeles\n"
            "  [b]d[/]         - Duplicar archivo/carpeta\n"
            "  [b]t[/]         - Crear archivo vacío con timestamp\n"
            "  [b]Delete[/]    - Eliminar elemento seleccionado\n\n"
            "[substantive]General:[/]\n"
            "  [b]?[/]         - Mostrar/Ocultar esta ayuda\n"
            "  [b]F5[/]        - Refresca el arbol de archivos\n"
            "  [b]q[/]         - Salir de la aplicación\n\n"
            "[dim]Presiona cualquier tecla asignada o ESC para cerrar[/]"
        )

        yield Grid(
            Label("AYUDA", id="help_title"),
            Static(texto_ayuda, id="help_content"),
            id="help_dialog",
        )


class VentanaNombres(ModalScreen[str | None]):  # ventana que pedira nombres, ect...
    def __init__(self, placeholder_text: str = "Nombre: ", **kwargs):
        super().__init__(**kwargs)
        self.placeholder_text = placeholder_text  # texto que se muestra en el input

    def compose(self) -> ComposeResult:
        yield Grid(  # pide el nombre al usuario -> lo guarda en la id
            Input(placeholder=self.placeholder_text, id="folder_name"),
            id="modal_dialog",
        )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()  # Quita espacios al inicio y final
        self.dismiss(
            value if value else None
        )  # cierra ventana y regresa valores, o None si vacio


class VentanaVisualizador(ModalScreen):  # ventana para ver contenido de archivos
    # Atajos para cerrar rápidamente
    BINDINGS: ClassVar[list[Binding]] = [Binding("escape,q,v", "dismiss", "Cerrar")]

    def __init__(self, filename: str, content: str, **kwargs):
        super().__init__(**kwargs)
        self.filename = filename  # guarda el nombre del archivo
        self.content = content  # guarda el contenido a mostrar

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(f"Contenido de: {self.filename}", id="help_title"),
            Static(self.content, id="help_content", expand=True),
            id="help_dialog",
        )


class VentanaPropiedades(ModalScreen):  # ventana para ver info detallada del archivo
    # Atajos para cerrar
    BINDINGS: ClassVar[list[Binding]] = [Binding("escape,q,p", "dismiss", "Cerrar")]

    def __init__(self, file_path: Path, **kwargs):
        super().__init__(**kwargs)
        self.file_path = file_path

    def compose(self) -> ComposeResult:
        # Obtenemos toda la info del archivo:
        try:
            stat = self.file_path.stat()  # obtenemos metadatos del archivo
            size = stat.st_size  # tamaño en bytes
            size_str = self._format_size(size)  # convertimos a formato legible
            perms = oct(stat.st_mode)[-3:]  # permisos en octal (ej: 644)
            modified = self._format_time(stat.st_mtime)  # fecha de modificacion
            created = self._format_time(stat.st_ctime)  # fecha de creacion
            tipo = "Carpeta" if self.file_path.is_dir() else "Archivo"
            extension = self.file_path.suffix if self.file_path.suffix else "Ninguna"

            info = (
                f"[bold]Propiedades de:[/] {self.file_path.name}\n\n"
                f"[substantive]Ruta completa:[/] {self.file_path.resolve()}\n"
                f"[substantive]Tipo:[/] {tipo}\n"
                f"[substantive]Tamaño:[/] {size_str} ({size:,} bytes)\n"
                f"[substantive]Extensión:[/] {extension}\n"
                f"[substantive]Permisos:[/] {perms}\n"
                f"[substantive]Modificado:[/] {modified}\n"
                f"[substantive]Creado:[/] {created}\n"
            )
        except Exception as e:
            info = f"[red]Error al obtener propiedades: {e}[/]"

        yield Grid(
            Label("PROPIEDADES", id="help_title"),
            Static(info, id="help_content"),
            id="help_dialog",
        )

    def _format_size(self, size: float) -> str:  # convierte bytes a human readable
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024  # dividimos entre 1024 para la siguiente unidad
        return f"{size:.2f} PB"

    def _format_time(self, timestamp: float) -> str:  # formatea fecha
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
