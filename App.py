# se importan las librerias a usar:
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, Footer, Header, Input, Label, Static


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
    BINDINGS = [Binding("escape,?,q", "dismiss", "Cerrar Ayuda")]

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
    BINDINGS = [Binding("escape,q,v", "dismiss", "Cerrar")]

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
    BINDINGS = [Binding("escape,q,p", "dismiss", "Cerrar")]

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


class Administrador(App):  # iniciamos la app
    BINDINGS = [  # las keys que se usaran, con su definicion:
        Binding(key="q", action="quit", description="Quit the app"),
        Binding(
            key="question_mark",
            action="help",
            description="Show help screen",
            key_display="?",
        ),
        Binding(key="delete", action="delete", description="Delete the thing"),
        Binding(key="j", action="down", description="Scroll down", show=False),
        Binding(key="k", action="up", description="Scroll up", show=False),
        Binding(key="n", action="create_folder", description="New Folder"),
        Binding(key="N", action="create_file", description="New File"),
        Binding(key="r", action="rename", description="Rename"),
        Binding(key="m", action="move", description="Move"),
        Binding(key="c", action="copy", description="Copy"),
        Binding(key="v", action="view", description="View file content"),
        Binding(key="e", action="edit", description="Edit with $EDITOR"),
        Binding(key="o", action="open_external", description="Open with default app"),
        Binding(key="p", action="properties", description="Properties"),
        Binding(key="z", action="zip_compress", description="Compress to zip"),
        Binding(key="Z", action="zip_extract", description="Extract zip"),
        Binding(key="y", action="copy_path", description="Copy path to clipboard"),
        Binding(key="d", action="duplicate", description="Duplicate"),
        Binding(key="t", action="touch_timestamp", description="Touch with timestamp"),
        Binding(key="f5", action="refresh", description="Refresh Tree"),
    ]
    CSS_PATH = "styles.css"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tree = None  # aqui guardaremos el DirectoryTree

    def compose(self) -> ComposeResult:  # lo que se "Imprimira" en la terminal:
        self._tree = DirectoryTree("./")  # creamos el arbol y lo guardamos
        yield self._tree
        yield Footer()
        yield Header()

    # definimos las acciones que se habian asignado en el bindings:
    ###### definicion de acciones ######

    def action_down(self) -> None:  # j -> baja
        if self._tree:  # si el arbol existe
            self._tree.action_cursor_down()  # baja el cursor una vez

    def action_up(self) -> None:  # k -> sube
        if self._tree:  # si el arbol existe
            self._tree.action_cursor_up()  # sube el cursor una vez

    def action_help(self) -> None:  # ? -> menu de help
        self.push_screen(VentanaAyuda())

    def action_refresh(self) -> None:  # F5 -> refresca el arbol
        if self._tree:
            self._refrescar_arbol()  # usamos el helper centralizado
            self.notify("Árbol de archivos actualizado")

    # --- Helpers reutilizables (nuevos) ---

    def _get_selected_path(self) -> Path | None:  # obtiene el path del cursor
        if not self._tree:  # si no hay arbol -> None
            return None
        node = self._tree.cursor_node  # guarda la ruta del cursor
        if node is None or node.data is None:  # no hay nada seleccionado
            return None
        return node.data.path  # regresa el path del nodo

    def _get_base_dir(self) -> Path:  # determina en que carpeta crear archivos/carpetas
        current_path = self._get_selected_path()  # ve que hay seleccionado
        if current_path:  # Hay algo seleccionado?:
            # El path es de un archivo o de una carpeta:
            return current_path.parent if current_path.is_file() else current_path
        else:  # seleccion == none -> usara la raiz:
            return Path("./")

    def _resolve_path(self, user_input: str) -> Path:  # resuelve rutas del usuario
        path = Path(user_input.strip())  # quita espacios y crea Path
        # Si el usuario usa ~ (home), lo expandimos:
        if str(path).startswith("~"):
            path = Path.home() / str(path)[1:].lstrip("/\\")
        return path.resolve()  # convierte a ruta absoluta

    def _sanitize_name(self, name: str) -> str:  # Remplaza errores del usuario
        # Sanitiza nombres de archivo para prevenir path traversal
        # Elimina caracteres de path y normaliza
        name = name.replace("\\", "").replace("/", "").replace("..", "")
        # Elimina caracteres nulos y de control
        name = "".join(c for c in name if c.isprintable() and c != "\x00")
        name = name.strip()
        if not name or name in (".", ".."):
            raise ValueError("Nombre inválido")
        return name

    def _refrescar_arbol(self) -> None:  # Fuerza refresco
        if not self._tree:  # si no hay arbol, no hace nada
            return
        node = self._tree.cursor_node
        if node and node.parent:
            self._tree.reload_node(node.parent)
        else:
            self._tree.reload()

    def _run_command(
        self, cmd: list[str], success_msg: str
    ) -> None:  # ejecuta comando externo
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.notify(success_msg)
        except subprocess.CalledProcessError as e:
            self.notify(f"Error: {e.stderr or e}", severity="error")
        except FileNotFoundError:
            self.notify("Comando no encontrado. ¿Está instalado?", severity="error")
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")

    def _run_command_nonblocking(self, cmd: list[str], success_msg: str) -> None:
        # Ejecuta un comando sin bloquear el event loop de Textual
        # Usamos Popen con stdout/stderr a DEVNULL para no bloquear
        try:
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,  # desvincula el proceso de la terminal
            )
            self.notify(success_msg)
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")

    # --- Acciones de archivos ---

    def action_delete(self) -> None:  # Del -> elimina
        target_path = self._get_selected_path()  # guarda la ruta actual

        if not target_path:  # no hay nada -> se sale de la funcion
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        try:
            if target_path.is_file():  # si es archivo
                os.remove(target_path)  # Borra el archivo
                self.notify(f"Archivo eliminado: {target_path.name}")
                self._refrescar_arbol()

            elif target_path.is_dir():  # si es Carpeta
                try:
                    os.rmdir(target_path)  # Intenta borrarla si está vacía
                    self.notify(f"Carpeta vacía eliminada: {target_path.name}")
                    self._refrescar_arbol()

                except OSError:  # Si la carpeta NO está vacía, saltará este error
                    # Definimos qué hacer cuando el usuario responda al modal
                    def procesar_confirmacion(confirmado: bool | None) -> None:
                        if confirmado:
                            try:
                                shutil.rmtree(
                                    target_path
                                )  # Borra la carpeta y TODO su contenido
                                self.notify(
                                    f"Carpeta y contenido eliminados: {target_path.name}"
                                )
                                self._refrescar_arbol()
                            except Exception as error_shutil:
                                self.notify(
                                    f"Error al eliminar contenido: {error_shutil}",
                                    severity="error",
                                )
                        else:
                            self.notify("Eliminación cancelada.")

                    # Lanzamos el modal de confirmación pasándole la función callback
                    self.push_screen(
                        VentanaConfirmacion(
                            f"La carpeta '{target_path.name}' contiene información. ¿Eliminar todo?"
                        ),
                        procesar_confirmacion,
                    )

        except Exception as e:  # en caso de otro tipo de error:
            self.notify(f"Error al eliminar: {e}", severity="error")

    def action_move(self) -> None:  # m -> Mover archivo o carpeta
        current_path = self._get_selected_path()  # guarda la ruta del cursor

        # 1. Validación: Verificar si hay algo seleccionado
        if not current_path:
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        # 2. Callback que se ejecuta cuando el usuario escribe el destino en el Modal
        def on_modal_close(destination_input: str | None) -> None:
            if not destination_input:
                return  # Si cancela o está vacío, no hace nada

            # Convertimos la entrada del usuario en un objeto Path resuelto
            target = self._resolve_path(destination_input)

            # Si el usuario da una ruta de carpeta, mantenemos el nombre original del archivo
            if target.is_dir() or destination_input.rstrip().endswith(("/", "\\")):
                new_path = target / current_path.name
            else:
                new_path = target

            # Validación: no mover sobre sí mismo
            if new_path.resolve() == current_path.resolve():
                self.notify(
                    "No se puede mover un archivo sobre sí mismo.", severity="error"
                )
                return

            # Validación de seguridad: prevenir salir del árbol de trabajo
            try:
                new_path.relative_to(Path(".").resolve())
            except ValueError:
                self.notify(
                    "No se permite mover fuera del directorio de trabajo.",
                    severity="error",
                )
                return

            try:
                # Aseguramos que las carpetas del destino existan antes de mover
                new_path.parent.mkdir(parents=True, exist_ok=True)

                # Movemos el archivo o directorio
                current_path.rename(new_path)

                self.notify(f"Movido con éxito a: {new_path}")
                self._refrescar_arbol()

            except FileExistsError:  # en caso de que ya exista:
                self.notify(
                    "Error: Ya existe un archivo en el destino.", severity="error"
                )
            except Exception as e:  # en caso de otro error:
                self.notify(f"Error al mover: {e}", severity="error")

        # 3. Abrimos el modal. Reutilizamos VentanaNombres con placeholder descriptivo.
        self.push_screen(
            VentanaNombres("Ruta destino (ej: ~/Documentos/ o ./carpeta/nuevo.txt): "),
            on_modal_close,
        )

    def action_create_folder(self) -> None:  # n -> makedir
        base_dir = self._get_base_dir()  # ve en que carpeta crear

        def on_modal_close(folder_name: str | None) -> None:
            if not folder_name:  # si no escribio el nombre:
                return  # salir

            try:
                safe_name = self._sanitize_name(folder_name)
            except ValueError:
                self.notify("Nombre de carpeta inválido.", severity="error")
                return

            new_folder_path = base_dir / safe_name  # crea la ruta de la carpeta nueva

            try:
                os.makedirs(new_folder_path, exist_ok=False)  # crea la carpeta
                self.notify(f"Carpeta creada: {safe_name}")  # mensaje

                self._refrescar_arbol()
            except FileExistsError:  # si el archivo existe:
                self.notify(
                    "Error: Ya existe una carpeta con ese nombre.", severity="error"
                )
            except Exception as e:  # Cualquier otro error:
                self.notify(f"Error al crear carpeta: {e}", severity="error")

        # le mostramos la ventana de input y le damos el mensaje que mostramos:
        self.push_screen(
            VentanaNombres("Nombre de la nueva carpeta: "),
            on_modal_close,
        )

    def action_create_file(self) -> None:  # N -> new file
        base_dir = self._get_base_dir()  # ve en que carpeta crear

        def on_modal_close(file_name: str | None) -> None:
            if not file_name:  # si no escribio el nombre:
                return  # salir

            try:
                safe_name = self._sanitize_name(file_name)
            except ValueError:
                self.notify("Nombre de archivo inválido.", severity="error")
                return

            new_file_path = base_dir / safe_name  # crea la ruta del archivo nuevo

            try:
                # Crea carpetas intermedias si no existen
                new_file_path.parent.mkdir(parents=True, exist_ok=True)
                new_file_path.touch(exist_ok=False)  # crea el archivo
                self.notify(f"Archivo creado: {safe_name}")  # mensaje

                self._refrescar_arbol()
            except FileExistsError:  # si el archivo existe:
                self.notify(
                    "Error: Ya existe un archivo con ese nombre.", severity="error"
                )
            except Exception as e:  # Cualquier otro error:
                self.notify(f"Error al crear archivo: {e}", severity="error")

        # le mostramos la ventana de input y le damos el mensaje que mostramos:
        self.push_screen(
            VentanaNombres("Nombre del nuevo archivo con su extensión: "),
            on_modal_close,
        )

    def action_copy(self) -> None:  # c -> Copiar archivo o carpeta
        current_path = self._get_selected_path()  # guarda la ruta del cursor

        # 1. Validación: Verificar si hay algo seleccionado
        if not current_path:
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        # 2. Callback cuando el usuario ingresa el destino en el Modal
        def on_modal_close(destination_input: str | None) -> None:
            if not destination_input:
                return  # Si cancela, no hace nada

            target = self._resolve_path(destination_input)

            # Si el destino es una carpeta existente o termina en separador, mantenemos el nombre original
            if target.is_dir() or destination_input.rstrip().endswith(("/", "\\")):
                new_path = target / current_path.name
            else:
                new_path = target

            # Validación: no copiar sobre sí mismo
            if new_path.resolve() == current_path.resolve():
                self.notify(
                    "No se puede copiar un archivo sobre sí mismo.", severity="error"
                )
                return

            # Validación de seguridad
            try:
                new_path.relative_to(Path(".").resolve())
            except ValueError:
                self.notify(
                    "No se permite copiar fuera del directorio de trabajo.",
                    severity="error",
                )
                return

            try:
                # Aseguramos que las carpetas del destino existan
                new_path.parent.mkdir(parents=True, exist_ok=True)

                # 3. Realizar la copia dependiendo de si es archivo o directorio
                if current_path.is_file():
                    shutil.copy2(
                        current_path, new_path
                    )  # Copia archivo manteniendo metadatos
                elif current_path.is_dir():
                    if new_path.exists():  # validamos que no exista ya
                        raise FileExistsError(f"Ya existe: {new_path}")
                    shutil.copytree(
                        current_path, new_path
                    )  # Copia carpetas de forma recursiva

                self.notify(f"Copiado con éxito a: {new_path}")
                self._refrescar_arbol()

            except FileExistsError:
                self.notify(
                    "Error: Ya existe un elemento en el destino.", severity="error"
                )
            except Exception as e:
                self.notify(f"Error al copiar: {e}", severity="error")

        # 4. Abrimos el modal reutilizando VentanaNombres
        self.push_screen(
            VentanaNombres("Digite la carpeta destino del clon: "), on_modal_close
        )

    def action_view(self) -> None:  # v -> ver archivo
        current_path = self._get_selected_path()  # ve directorio del puntero

        if not current_path:  # Si no hay nada seleccionado
            self.notify("No hay ningún archivo seleccionado", severity="warning")
            return

        if current_path.is_dir():  # si es una carpeta
            self.notify("No se puede visualizar una carpeta", severity="warning")
            return

        # Validación: no abrir archivos binarios grandes
        max_size = 5 * 1024 * 1024  # 5 MB limite
        try:
            file_size = current_path.stat().st_size  # vemos el tamaño
            if file_size > max_size:  # si es muy grande
                self.notify(
                    f"Archivo demasiado grande ({file_size / 1024 / 1024:.1f} MB). "
                    "Máximo permitido: 5 MB",
                    severity="warning",
                )
                return

            # abrimos el archivo en read y vemos los primeros 50k de caracteres
            with open(current_path, "r", encoding="utf-8", errors="replace") as f:
                contenido = f.read(50_000)

            # Usamos la clase VentanaVisualizador de nivel superior
            self.push_screen(VentanaVisualizador(current_path.name, contenido))

        except UnicodeDecodeError:  # si es binario
            self.notify(
                "El archivo parece ser binario y no puede mostrarse.",
                severity="warning",
            )
        except Exception as e:
            self.notify(f"No se pudo leer el archivo: {e}", severity="error")

    def action_rename(self) -> None:  # r -> Rename
        current_path = self._get_selected_path()  # guarda la ruta del cursor

        # en caso este vacio:
        if not current_path:  # no hay nada -> se sale de la funcion
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        # acceda a la ventana de rename:
        def on_modal_close(new_name: str | None) -> None:
            if not new_name:  # en caso de que este vacio
                return  # salir

            try:
                safe_name = self._sanitize_name(new_name)
            except ValueError:
                self.notify("Nombre inválido.", severity="error")
                return

            new_path = current_path.with_name(safe_name)

            # Validacion: no renombrar si ya existe otro con ese nombre
            if new_path.exists() and new_path.resolve() != current_path.resolve():
                self.notify(
                    "Error: Ya existe un archivo/carpeta con ese nombre",
                    severity="error",
                )
                return

            try:  # el codigo que cambia el nombre:
                current_path.rename(new_path)
                self.notify(f"Renombrado a: {safe_name}")  # mensaje
                self._refrescar_arbol()

            except FileExistsError:  # si el archivo existe:
                self.notify(
                    "Error: Ya existe un archivo/carpeta con ese nombre",
                    severity="error",
                )
            except Exception as e:  # Cualquier otro error:
                self.notify(f"Error al renombrar: {e}", severity="error")

        # abre la ventana de input y le damos el mensaje que mostrara:
        self.push_screen(
            VentanaNombres("Nuevo nombre completo (con extensión si aplica): "),
            on_modal_close,
        )

    def action_edit(self) -> None:  # e -> Abrir archivo en $EDITOR
        current_path = self._get_selected_path()  # ve que hay seleccionado

        if not current_path:  # no hay nada
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        if current_path.is_dir():  # si es carpeta
            self.notify("No se puede editar una carpeta.", severity="warning")
            return

        # Obtenemos el editor del sistema (vi, nano, code, etc.)
        editor = os.environ.get("EDITOR", "vi")  # por defecto vi si no hay $EDITOR

        # Determinamos si es un editor de terminal o GUI
        # Los editores de terminal necesitan que Textual se suspenda temporalmente
        # porque compiten por el mismo terminal
        terminal_editors = {"vi", "vim", "nvim", "nano", "emacs", "micro", "joe"}
        editor_name = os.path.basename(editor).lower()

        if editor_name in terminal_editors:
            # Para editores de terminal (vi, nano, etc.):
            # Textual debe ceder el control del terminal al editor
            # Usamos suspend() que detiene la app, ejecuta el comando,
            # y al cerrar el editor, la app se reanuda automaticamente
            try:
                # suspend() pausa Textual, ejecuta el comando en el terminal,
                # y cuando termina, restaura la UI automaticamente
                # self.suspend(lambda: os.system(f'{editor} "{current_path}"')) # linea original
                self.suspend()
                self.notify(f"Archivo editado: {current_path.name}")
                self._refrescar_arbol()
            except Exception as e:
                self.notify(f"Error al abrir editor: {e}", severity="error")
        else:
            # Para editores GUI (code, sublime, etc.):
            # No compiten por el terminal, asi que los lanzamos en background
            # con Popen para no bloquear la UI
            self._run_command_nonblocking(
                [editor, str(current_path)], f"Archivo abierto en {editor}"
            )

    def action_open_external(self) -> None:  # o -> Abrir con app predeterminada
        current_path = self._get_selected_path()  # ve que hay seleccionado

        if not current_path:  # no hay nada
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        # Usamos xdg-open (Linux), open (macOS) o startfile (Windows)
        # Estos comandos lanzan la app predeterminada y retornan
        if sys.platform == "darwin":  # macOS
            self._run_command_nonblocking(
                ["open", str(current_path)], f"Abierto: {current_path.name}"
            )
        elif sys.platform == "win32":  # Windows
            try:
                # os.startfile no bloquea, es la forma nativa de Windows
                os.startfile(str(current_path))
                self.notify(f"Abierto: {current_path.name}")
            except OSError as e:
                self.notify(f"No se pudo abrir: {e}", severity="error")
        else:  # Linux y otros
            # xdg-open puede quedarse esperando si la app escribe a stdout
            # Por eso redirigimos a DEVNULL y no esperamos
            self._run_command_nonblocking(
                ["xdg-open", str(current_path)], f"Abierto: {current_path.name}"
            )

    def action_properties(self) -> None:  # p -> Ver propiedades del archivo
        current_path = self._get_selected_path()  # ve que hay seleccionado

        if not current_path:  # no hay nada
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        # Abrimos la ventana de propiedades con toda la info
        self.push_screen(VentanaPropiedades(current_path))

    def action_zip_compress(self) -> None:  # z -> Comprimir a .zip
        current_path = self._get_selected_path()  # ve que hay seleccionado

        if not current_path:  # no hay nada
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        # El nombre del zip sera el nombre original + .zip
        zip_name = f"{current_path.name}.zip"
        zip_path = current_path.parent / zip_name

        # Si ya existe un zip con ese nombre, agregamos numero
        counter = 1
        while zip_path.exists():
            zip_name = f"{current_path.name}_{counter}.zip"
            zip_path = current_path.parent / zip_name
            counter += 1

        try:
            with ZipFile(zip_path, "w") as zf:
                if current_path.is_file():  # si es archivo
                    zf.write(current_path, current_path.name)
                else:  # si es carpeta, comprimimos todo recursivamente
                    for file_path in current_path.rglob("*"):
                        if file_path.is_file():
                            # arcname es el nombre dentro del zip
                            # relative_to(current_path) hace que la estructura
                            # dentro del zip sea correcta, sin niveles extra
                            arcname = file_path.relative_to(current_path)
                            zf.write(file_path, arcname)

            self.notify(f"Comprimido: {zip_name}")
            self._refrescar_arbol()

        except Exception as e:
            self.notify(f"Error al comprimir: {e}", severity="error")

    def action_zip_extract(self) -> None:  # Z -> Descomprimir .zip
        current_path = self._get_selected_path()  # ve que hay seleccionado

        if not current_path:  # no hay nada
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        if current_path.suffix.lower() != ".zip":  # si no es zip
            self.notify("El archivo seleccionado no es un .zip", severity="warning")
            return

        # Carpeta destino sera el nombre del zip sin extension
        extract_dir = current_path.with_suffix("")

        # Si ya existe, agregamos numero
        counter = 1
        original_name = extract_dir.name
        while extract_dir.exists():
            extract_dir = current_path.parent / f"{original_name}_{counter}"
            counter += 1

        try:
            with ZipFile(current_path, "r") as zf:
                # Validacion de seguridad contra Zip Slip
                # Un zip malicioso puede contener rutas como ../../../etc/passwd
                # que al extraerse escribirian fuera del directorio destino
                for member in zf.namelist():
                    member_path = extract_dir / member
                    try:
                        # relative_to lanza ValueError si member_path no esta
                        # dentro de extract_dir, detectando el ataque
                        member_path.relative_to(extract_dir.resolve())
                    except ValueError:
                        raise ValueError(
                            f"Archivo malicioso en zip detectado: {member}"
                        )

                zf.extractall(extract_dir)

            self.notify(f"Extraído en: {extract_dir.name}")
            self._refrescar_arbol()

        except Exception as e:
            self.notify(f"Error al extraer: {e}", severity="error")

    def action_copy_path(self) -> None:  # y -> Copiar ruta al portapapeles
        current_path = self._get_selected_path()  # ve que hay seleccionado

        if not current_path:  # no hay nada
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        ruta = str(current_path.resolve())  # ruta absoluta

        try:
            # Intentamos usar xclip (Linux), pbcopy (macOS) o clip (Windows)
            if sys.platform == "darwin":  # macOS
                subprocess.run(["pbcopy"], input=ruta, text=True, check=True)
            elif sys.platform == "win32":  # Windows
                subprocess.run(["clip"], input=ruta, text=True, check=True)
            else:  # Linux - intentamos xclip o wl-copy
                try:
                    subprocess.run(
                        ["xclip", "-selection", "clipboard"],
                        input=ruta,
                        text=True,
                        check=True,
                    )
                except FileNotFoundError:
                    subprocess.run(["wl-copy"], input=ruta, text=True, check=True)

            self.notify(f"Ruta copiada: {ruta}")

        except Exception as e:
            # Si no hay herramienta de clipboard, mostramos la ruta para copiar manual
            self.notify(
                f"Clipboard no disponible. Ruta: {ruta}\nError: {e}", severity="warning"
            )

    def action_duplicate(self) -> None:  # d -> Duplicar archivo/carpeta
        current_path = self._get_selected_path()  # ve que hay seleccionado

        if not current_path:  # no hay nada
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        # Creamos el nombre del duplicado: archivo.txt -> archivo (copia).txt
        if current_path.is_file():
            new_name = f"{current_path.stem} (copia){current_path.suffix}"
        else:
            new_name = f"{current_path.name} (copia)"

        new_path = current_path.parent / new_name

        # Si ya existe, agregamos numero
        counter = 1
        while new_path.exists():
            if current_path.is_file():
                new_name = f"{current_path.stem} (copia {counter}){current_path.suffix}"
            else:
                new_name = f"{current_path.name} (copia {counter})"
            new_path = current_path.parent / new_name
            counter += 1

        try:
            if current_path.is_file():
                shutil.copy2(current_path, new_path)
            else:
                shutil.copytree(current_path, new_path)

            self.notify(f"Duplicado: {new_name}")
            self._refrescar_arbol()

        except Exception as e:
            self.notify(f"Error al duplicar: {e}", severity="error")

    def action_touch_timestamp(self) -> None:  # t -> Crear archivo con timestamp
        base_dir = self._get_base_dir()  # ve en que carpeta crear

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # fecha y hora actual
        file_name = f"archivo_{timestamp}.txt"  # nombre con timestamp

        new_file_path = base_dir / file_name

        try:
            new_file_path.touch()  # crea el archivo vacio
            self.notify(f"Archivo creado: {file_name}")
            self._refrescar_arbol()

        except Exception as e:
            self.notify(f"Error al crear archivo: {e}", severity="error")


if __name__ == "__main__":
    app = Administrador()
    app.run()
