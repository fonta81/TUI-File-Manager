# ==============================================================================
# PANTALLAS MODALES DE LA INTERFAZ DE USUARIO (Screens)
# ==============================================================================
# Este módulo define todas las ventanas emergentes (diálogos modales) de la app.
# En Textual, un 'ModalScreen' es una pantalla que se superpone sobre la principal
# y detiene o captura el foco del usuario hasta que se cierra (dismiss).

from datetime import datetime
from pathlib import Path
from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Static


# ------------------------------------------------------------------------------
# 1. VENTANA DE CONFIRMACIÓN (S/N)
# ------------------------------------------------------------------------------
# Esta ventana solicita confirmación del usuario para acciones críticas (ej: borrar carpetas).
# Retorna un valor booleano (True para Sí, False para No) cuando se cierra.
class VentanaConfirmacion(ModalScreen[bool]):
    
    # El constructor recibe el mensaje personalizado que se le mostrará al usuario
    def __init__(self, mensaje: str, **kwargs):
        super().__init__(**kwargs)
        self.mensaje = mensaje  # Guardamos el mensaje para poder usarlo en compose()

    # El método compose() define la estructura de widgets que se dibujará en pantalla
    def compose(self) -> ComposeResult:
        # Preparamos el texto del cuerpo con formato usando la sintaxis de marcado de Rich
        texto_instrucciones = (
            f"{self.mensaje}\n\n"
            "[dim]Presiona [b]S[/b] para confirmar, [b]N[/b] o [b]Esc[/b] para cancelar.[/]"
        )
        
        # Devolvemos un contenedor Grid que distribuye sus elementos internamente
        yield Grid(
            Label("CONFIRMACIÓN", id="modal_title"),  # Título llamativo arriba
            Static(texto_instrucciones, id="modal_content"),  # Contenido del mensaje explicativo
            id="modal_dialog",  # ID utilizado para aplicar el estilo visual CSS (styles.tcss)
        )

    # El método 'on_key' captura directamente los eventos de pulsación de teclas del teclado.
    # Esto nos permite responder de inmediato a una sola tecla sin requerir un cuadro de texto ni Enter.
    def on_key(self, event) -> None:
        key = event.key.lower()  # Convertimos a minúsculas para comparar de forma uniforme
        
        if key == "s":
            # Si presiona S, cerramos el modal devolviendo True (Confirmado)
            self.dismiss(True)
        elif key in ("n", "escape"):
            # Si presiona N o Escape, cerramos el modal devolviendo False (Cancelado)
            self.dismiss(False)


# ------------------------------------------------------------------------------
# 2. VENTANA DE AYUDA (Atajos de teclado)
# ------------------------------------------------------------------------------
# Esta ventana muestra la lista de comandos y atajos de teclado disponibles.
class VentanaAyuda(ModalScreen):
    
    # Definimos atajos específicos dentro del modal para que el usuario pueda cerrarlo
    # presionando Escape, la tecla de interrogación (?) o la tecla q de forma rápida.
    # El método 'dismiss' es una acción nativa de Textual para cerrar pantallas.
    BINDINGS: ClassVar[list[Binding]] = [
        Binding("escape,?,q", "dismiss", "Cerrar Ayuda")
    ]

    # Construimos la interfaz de la ayuda
    def compose(self) -> ComposeResult:
        # Texto formateado con marcas de Rich para resaltar los atajos de teclado en negrita
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

        # Retornamos el Grid para renderizar el panel de ayuda
        yield Grid(
            Label("AYUDA", id="help_title"),
            Static(texto_ayuda, id="help_content"),
            id="help_dialog",
        )


# ------------------------------------------------------------------------------
# 3. VENTANA PARA ENTRADA DE TEXTO / NOMBRES
# ------------------------------------------------------------------------------
# Esta ventana solicita al usuario que ingrese un nombre de archivo, carpeta o ruta.
# Retorna un String con la entrada del usuario, o None si canceló o lo dejó vacío.
class VentanaNombres(ModalScreen[str | None]):
    
    # El constructor recibe un texto marcador de posición (placeholder) descriptivo
    def __init__(self, placeholder_text: str = "Nombre: ", **kwargs):
        super().__init__(**kwargs)
        self.placeholder_text = placeholder_text  # Lo almacenamos en el objeto

    # Diseñamos la interfaz con un cuadro de entrada de texto enfocado automáticamente
    def compose(self) -> ComposeResult:
        yield Grid(
            # El widget Input permite al usuario teclear. Le pasamos el placeholder.
            Input(placeholder=self.placeholder_text, id="folder_name"),
            id="modal_dialog",
        )

    # Este método se dispara automáticamente cuando el usuario presiona Enter en el Input
    def on_input_submitted(self, event: Input.Submitted) -> None:
        # Obtenemos el valor de la caja de texto y eliminamos espacios innecesarios
        value = event.value.strip()
        
        # Cerramos la pantalla retornando el string escrito (o None si estaba vacío)
        self.dismiss(value if value else None)


# ------------------------------------------------------------------------------
# 4. VENTANA VISUALIZADORA DE TEXTO
# ------------------------------------------------------------------------------
# Esta ventana permite examinar los contenidos de un archivo de texto en pantalla completa.
class VentanaVisualizador(ModalScreen):
    
    # Teclas rápidas para cerrar la visualización de manera inmediata y cómoda
    BINDINGS: ClassVar[list[Binding]] = [Binding("escape,q,v", "dismiss", "Cerrar")]

    # El constructor recibe el nombre del archivo y el texto de su contenido ya leído
    def __init__(self, filename: str, content: str, **kwargs):
        super().__init__(**kwargs)
        self.filename = filename  # Nombre del archivo para mostrar en el título
        self.content = content    # Texto plano a renderizar

    # Maquetamos el visor usando un Label de título y un bloque estático desplazable
    def compose(self) -> ComposeResult:
        yield Grid(
            Label(f"Contenido de: {self.filename}", id="help_title"),
            Static(self.content, id="help_content", expand=True),  # expand=True llena el espacio
            id="help_dialog",
        )


# ------------------------------------------------------------------------------
# 5. VENTANA DE PROPIEDADES Y METADATOS
# ------------------------------------------------------------------------------
# Esta ventana muestra información muy completa y detallada sobre el archivo seleccionado.
class VentanaPropiedades(ModalScreen):
    
    # Atajos de teclado rápidos para salir de esta pantalla de propiedades
    BINDINGS: ClassVar[list[Binding]] = [Binding("escape,q,p", "dismiss", "Cerrar")]

    # El constructor recibe la ruta Path del archivo del cual deseamos ver detalles
    def __init__(self, file_path: Path, **kwargs):
        super().__init__(**kwargs)
        self.file_path = file_path  # Almacenamos el Path

    # Construimos y calculamos los metadatos en el compose() para renderizarlos
    def compose(self) -> ComposeResult:
        try:
            # Obtenemos los metadatos del archivo a través de la llamada del sistema .stat()
            stat = self.file_path.stat()
            
            size = stat.st_size  # Tamaño bruto en Bytes
            size_str = self._format_size(size)  # Formateamos a KB, MB, etc.
            
            # Formateamos los permisos en octal (ej: 0o755 -> nos quedamos con los últimos 3 dígitos '755')
            perms = oct(stat.st_mode)[-3:]
            
            # Convertimos las fechas UNIX timestamp a formato legible de texto local
            modified = self._format_time(stat.st_mtime)  # Fecha de modificación
            created = self._format_time(stat.st_ctime)    # Fecha de creación o de cambio de metadatos
            
            # Determinamos si el elemento en cuestión es una Carpeta o un Archivo de datos
            tipo = "Carpeta" if self.file_path.is_dir() else "Archivo"
            
            # Obtenemos la extensión del archivo, o indicamos 'Ninguna' si no la tiene
            extension = self.file_path.suffix if self.file_path.suffix else "Ninguna"

            # Construimos un string formateado con Rich que detalla cada metadato
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
            # En caso de ocurrir algún error (ej: permisos denegados), mostramos un mensaje de error estilizado
            info = f"[red]Error al obtener propiedades: {e}[/]"

        # Renderizamos el panel en pantalla
        yield Grid(
            Label("PROPIEDADES", id="help_title"),
            Static(info, id="help_content"),
            id="help_dialog",
        )

    # Helper privado que formatea una cantidad de bytes a una unidad humana comprensible
    def _format_size(self, size: float) -> str:
        # Iteramos sobre la lista de magnitudes dividiendo sucesivamente entre 1024
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.2f} {unit}"  # Si es menor que 1024, devolvemos la unidad actual
            size /= 1024
        return f"{size:.2f} PB"  # Si supera TeraBytes, retornamos PetaBytes

    # Helper privado que convierte una marca de tiempo timestamp a formato legible de fecha y hora
    def _format_time(self, timestamp: float) -> str:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
