# ==============================================================================
# CLASE PRINCIPAL DEL ADMINISTRADOR DE ARCHIVOS (App Class)
# ==============================================================================
# Este archivo contiene la lógica medular de la aplicación.
# Hereda de 'textual.app.App' para implementar el ciclo de vida, las acciones de
# teclado, la barra de estado y el árbol de carpetas de TexrualApp.

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import ClassVar
from zipfile import ZipFile

# Importamos las herramientas de interfaz de usuario de Textual
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Static

# Importamos el árbol de directorios con iconos personalizado
from .icon_tree import IconTree

# Importamos las clases de las pantallas de diálogo modales
from .screens import (
    VentanaAyuda,
    VentanaConfirmacion,
    VentanaNombres,
    VentanaPropiedades,
    VentanaVisualizador,
)


class Administrador(App):
    # --------------------------------------------------------------------------
    # MAPEADO DE TECLAS Y ATAJOS DE TECLADO (Bindings)
    # --------------------------------------------------------------------------
    # Aquí definimos qué teclas desencadenan qué acciones en nuestra app.
    # El formato es: Binding(tecla, acción, descripción, mostrar_en_barra, etc.)
    BINDINGS: ClassVar[list[Binding]] = [
        # q -> Llama a la acción 'quit' nativa de Textual para cerrar la aplicación
        Binding(key="q", action="quit", description="Salir"),
        
        # ? -> Llama a nuestra acción 'help' para abrir el modal de ayuda
        Binding(
            key="question_mark",
            action="help",
            description="Ayuda",
            key_display="?",
        ),
        
        # Delete -> Llama a la acción para eliminar el elemento seleccionado
        Binding(key="delete", action="delete", description="Eliminar"),
        
        # j/k -> Atajos típicos de Vim para desplazarse hacia abajo/arriba (ocultos de la barra inferior)
        Binding(key="j", action="down", description="Bajar", show=False),
        Binding(key="k", action="up", description="Subir", show=False),
        
        # n / N -> Crear carpeta / archivo vacíos respectivamente
        Binding(key="n", action="create_folder", description="Nueva Carpeta"),
        Binding(key="N", action="create_file", description="Nuevo Archivo"),
        
        # r -> Renombrar el elemento seleccionado
        Binding(key="r", action="rename", description="Renombrar"),
        
        # m -> Mover el elemento (cambiar su ubicación / ruta)
        Binding(key="m", action="move", description="Mover"),
        
        # c -> Copiar el elemento seleccionado a un nuevo destino
        Binding(key="c", action="copy", description="Copiar"),
        
        # v -> Visualizar el contenido de un archivo de texto en un modal interno
        Binding(key="v", action="view", description="Ver Contenido"),
        
        # e -> Abrir el archivo en el editor de texto configurado en el sistema ($EDITOR)
        Binding(key="e", action="edit", description="Editar"),
        
        # o -> Abrir usando la aplicación predeterminada del sistema operativo (ej: PDF, imágenes)
        Binding(key="o", action="open_external", description="Abrir Externo"),
        
        # p -> Mostrar propiedades y metadatos detallados (fechas, permisos, tamaño)
        Binding(key="p", action="properties", description="Propiedades"),
        
        # z / Z -> Comprimir a ZIP / Extraer archivo ZIP seleccionado
        Binding(key="z", action="zip_compress", description="Comprimir ZIP"),
        Binding(key="Z", action="zip_extract", description="Extraer ZIP"),
        
        # y -> Copiar la ruta absoluta del archivo/carpeta al portapapeles del sistema
        Binding(key="y", action="copy_path", description="Copiar Ruta"),
        
        # d -> Duplicar el elemento creando un clon en el mismo directorio
        Binding(key="d", action="duplicate", description="Duplicar"),
        
        # t -> Crear un archivo de texto vacío con la marca de tiempo actual en su nombre
        Binding(key="t", action="touch_timestamp", description="Crear con Fecha"),
        
        # F5 -> Recargar el nodo seleccionado del árbol para refrescar los cambios manuales
        Binding(key="f5", action="refresh", description="Actualizar Árbol"),
    ]

    # Ruta relativa al archivo de estilos CSS de Textual
    CSS_PATH = "../styles.tcss"

    # Constructor de la clase de la aplicación
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Inicializamos el atributo donde guardaremos la referencia al widget del árbol
        self._tree = None
        # Creamos una barra de estado inferior usando un widget estático
        self._status_bar = Static("Seleccione un archivo", id="status_bar")

    # --------------------------------------------------------------------------
    # CONSTRUCCIÓN DE LA INTERFAZ DE USUARIO (Compose)
    # --------------------------------------------------------------------------
    # Define el orden y disposición visual de los widgets al iniciar la app.
    def compose(self) -> ComposeResult:
        # 1. Instanciamos nuestro árbol con iconos apuntando al directorio actual ('./')
        self._tree = IconTree("./")
        # 2. Le damos el foco del teclado inmediatamente al árbol para poder navegar desde el segundo cero
        self._tree.focus()
        
        # 3. 'yield' entrega cada componente en orden vertical para ser renderizado:
        yield Header()        # Cabecera superior de la aplicación
        yield self._tree      # El árbol central de archivos
        yield self._status_bar # La barra de estado con información del archivo actual
        yield Footer()        # La barra inferior de atajos de teclado (Bindings)

    # --------------------------------------------------------------------------
    # EVENTO DE INTERFAZ: NODO DEL ÁRBOL RESALTADO (Node Highlighted)
    # --------------------------------------------------------------------------
    # Este método de evento se dispara automáticamente cada vez que el usuario se desplaza
    # y selecciona un elemento diferente en el árbol.
    def on_tree_node_highlighted(self, event: IconTree.NodeHighlighted) -> None:
        # Verificamos si el nodo actual tiene información de archivo cargada
        if event.node.data:
            path = event.node.data.path  # Extraemos la ruta (Path)
            info = f" {path.name}"       # Preparamos el mensaje básico con el nombre
            
            # Si es un archivo, obtenemos su tamaño y lo agregamos al mensaje informativo
            if path.is_file():
                info += f" ({path.stat().st_size} bytes)"
            
            # Actualizamos la barra de estado con la información del archivo actual
            self._status_bar.update(info)
        else:
            # Si el nodo no tiene datos válidos, limpiamos la barra con un mensaje por defecto
            self._status_bar.update(" Seleccione un archivo")

    # ==============================================================================
    # DEFINICIÓN DE ACCIONES ASOCIADAS A LOS ATADOS DE TECLADO (Keyboard Actions)
    # ==============================================================================

    # Acción de bajar en el árbol (tecla j)
    def action_down(self) -> None:
        if self._tree:
            # Llama al método nativo de DirectoryTree para desplazar el cursor hacia abajo
            self._tree.action_cursor_down()

    # Acción de subir en el árbol (tecla k)
    def action_up(self) -> None:
        if self._tree:
            # Llama al método nativo de DirectoryTree para desplazar el cursor hacia arriba
            self._tree.action_cursor_up()

    # Acción de ayuda (tecla ?)
    def action_help(self) -> None:
        # Muestra en primer plano (apila) la pantalla de la guía de ayuda
        self.push_screen(VentanaAyuda())

    # Acción de recarga (tecla F5)
    def action_refresh(self) -> None:
        if self._tree:
            # Forzamos la actualización visual del árbol
            self._refrescar_arbol()
            # Mostramos una notificación emergente en la esquina
            self.notify("Árbol de archivos actualizado")

    # ==============================================================================
    # MÉTODOS AUXILIARES REUTILIZABLES (Helper Methods)
    # ==============================================================================

    # Retorna el objeto Path del elemento que tiene actualmente el foco o cursor del árbol
    def _get_selected_path(self) -> Path | None:
        if not self._tree:
            return None
        # Extraemos el nodo bajo el cursor
        node = self._tree.cursor_node
        if node is None or node.data is None:
            return None
        # Devolvemos la ruta asociada al nodo
        return node.data.path

    # Determina en qué directorio se deben crear o colocar archivos/carpetas.
    # Si el cursor está en una carpeta, se usa esa misma. Si está en un archivo, se usa su carpeta contenedora (parent).
    def _get_base_dir(self) -> Path:
        current_path = self._get_selected_path()
        if current_path:
            # Si el elemento seleccionado es un archivo, devolvemos su directorio padre; si no, es una carpeta y la devolvemos directo
            return current_path.parent if current_path.is_file() else current_path
        else:
            # Si no hay selección válida, trabajamos sobre la raíz del directorio de trabajo
            return Path("./")

    # Convierte una ruta en string ingresada por el usuario (ej: ~/Descargas o ./archivo.txt) en un objeto Path resuelto y absoluto
    def _resolve_path(self, user_input: str) -> Path:
        path = Path(user_input.strip())  # Removemos espacios al inicio/final
        # Si el usuario utiliza el carácter tilde '~', lo expandimos a su carpeta de usuario personal (Home)
        if str(path).startswith("~"):
            path = Path.home() / str(path)[1:].lstrip("/\\")
        # Retornamos la ruta resuelta de forma absoluta para evitar inconsistencias de directorios relativos
        return path.resolve()

    # Sanitiza nombres de archivo proporcionados por el usuario para prevenir vulnerabilidades de escape de directorio (Path Traversal)
    def _sanitize_name(self, name: str) -> str:
        # Eliminamos secuencias que permitan retroceder de carpeta o especificar separadores
        name = name.replace("\\", "").replace("/", "").replace("..", "")
        # Removemos caracteres nulos o no imprimibles que puedan alterar el sistema de archivos
        name = "".join(c for c in name if c.isprintable() and c != "\x00")
        name = name.strip()
        # Si el nombre queda vacío o coincide con puntos de directorio, lanzamos un error de validación
        if not name or name in (".", ".."):
            raise ValueError("Nombre inválido")
        return name

    # Recarga un nodo del árbol para forzar a Textual a releer el disco y reflejar archivos nuevos/eliminados
    def _refrescar_arbol(self) -> None:
        if not self._tree:
            return
        node = self._tree.cursor_node
        # Si hay un nodo seleccionado y tiene un padre, recargamos el directorio padre para actualizar el listado entero
        if node and node.parent:
            self._tree.reload_node(node.parent)
        else:
            # Si no hay selección o es la raíz, recargamos el árbol completo desde la base
            self._tree.reload()

    # Ejecuta un comando externo de sistema de forma síncrona/bloqueante
    def _run_command(self, cmd: list[str], success_msg: str) -> None:
        try:
            # Ejecutamos el comando esperando a que termine y capturando errores si falla
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.notify(success_msg)  # Notificamos éxito
        except subprocess.CalledProcessError as e:
            # En caso de que el comando retorne un código de salida de error
            self.notify(f"Error: {e.stderr or e}", severity="error")
        except FileNotFoundError:
            # En caso de que el programa/comando no exista en el sistema
            self.notify("Comando no encontrado. ¿Está instalado?", severity="error")
        except Exception as e:
            # Capturamos cualquier otro fallo imprevisto
            self.notify(f"Error: {e}", severity="error")

    # Ejecuta un comando externo desvinculado (en segundo plano) para no congelar la interfaz de Textual
    def _run_command_nonblocking(self, cmd: list[str], success_msg: str) -> None:
        try:
            # Usamos subprocess.Popen para iniciar el proceso de fondo sin esperar su finalización
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,  # Redirigimos salidas de texto a la nada para evitar ruidos en terminal
                stderr=subprocess.DEVNULL,
                start_new_session=True,     # Desvinculamos el proceso del ciclo de vida de la terminal actual
            )
            self.notify(success_msg)
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")

    # ==============================================================================
    # ACCIONES DEL GESTOR DE ARCHIVOS (File Operations Actions)
    # ==============================================================================

    # Acción de Eliminar (tecla Delete)
    def action_delete(self) -> None:
        target_path = self._get_selected_path()

        # Si no hay selección, notificamos y cancelamos
        if not target_path:
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        try:
            if target_path.is_file():
                # 1. Si es un archivo de datos, lo removemos de forma directa
                os.remove(target_path)
                self.notify(f"Archivo eliminado: {target_path.name}")
                self._refrescar_arbol()

            elif target_path.is_dir():
                try:
                    # 2. Si es una carpeta, primero intentamos borrarla asumiendo que está vacía
                    os.rmdir(target_path)
                    self.notify(f"Carpeta vacía eliminada: {target_path.name}")
                    self._refrescar_arbol()
                except OSError:
                    # 3. Si arroja un error (típicamente porque la carpeta contiene archivos),
                    # abrimos un diálogo modal para solicitar confirmación del borrado recursivo.
                    
                    # Definimos el callback que procesará la respuesta del diálogo modal
                    def procesar_confirmacion(confirmado: bool | None) -> None:
                        if confirmado:
                            try:
                                # Borramos recursivamente la carpeta entera y todos sus hijos
                                shutil.rmtree(target_path)
                                self.notify(f"Carpeta y contenido eliminados: {target_path.name}")
                                self._refrescar_arbol()
                            except Exception as error_shutil:
                                self.notify(f"Error al eliminar contenido: {error_shutil}", severity="error")
                        else:
                            # Si el usuario seleccionó cancelar (N o Esc)
                            self.notify("Eliminación cancelada.")

                    # Mostramos la ventana de confirmación en primer plano
                    self.push_screen(
                        VentanaConfirmacion(
                            f"La carpeta '{target_path.name}' contiene información. ¿Eliminar todo?"
                        ),
                        procesar_confirmacion, # Pasamos la función callback para cuando se cierre
                    )

        except Exception as e:
            self.notify(f"Error al eliminar: {e}", severity="error")

    # Acción de Mover / Cortar (tecla m)
    def action_move(self) -> None:
        current_path = self._get_selected_path()

        # Validación inicial
        if not current_path:
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        # Callback que se ejecutará cuando el usuario proporcione el destino y presione Enter en la modal
        def on_modal_close(destination_input: str | None) -> None:
            if not destination_input:
                return  # Cancelado por el usuario

            # Resolvemos la entrada a una ruta absoluta
            target = self._resolve_path(destination_input)

            # Si el destino es una carpeta existente, movemos el archivo con su nombre original dentro de ella
            if target.is_dir() or destination_input.rstrip().endswith(("/", "\\")):
                new_path = target / current_path.name
            else:
                new_path = target

            # Protección: no permitir mover un elemento sobre sí mismo
            if new_path.resolve() == current_path.resolve():
                self.notify("No se puede mover un archivo sobre sí mismo.", severity="error")
                return

            # Protección de seguridad: evitar interactuar fuera del árbol de trabajo actual
            try:
                new_path.relative_to(Path(".").resolve())
            except ValueError:
                self.notify("No se permite mover fuera del directorio de trabajo.", severity="error")
                return

            try:
                # Nos aseguramos de que existan todos los directorios intermedios del destino
                new_path.parent.mkdir(parents=True, exist_ok=True)

                # Renombramos (movemos) el archivo físico en el disco
                current_path.rename(new_path)

                self.notify(f"Movido con éxito a: {new_path}")
                self._refrescar_arbol()  # Refrescamos el árbol

            except FileExistsError:
                self.notify("Error: Ya existe un archivo en el destino.", severity="error")
            except Exception as e:
                self.notify(f"Error al mover: {e}", severity="error")

        # Lanzamos la modal solicitando la ruta de destino al usuario
        self.push_screen(
            VentanaNombres("Ruta destino (ej: ~/Documentos/ o ./carpeta/nuevo.txt): "),
            on_modal_close, # Le pasamos el callback
        )

    # Acción de crear carpeta (tecla n)
    def action_create_folder(self) -> None:
        # Obtenemos el directorio donde crearemos la nueva carpeta
        base_dir = self._get_base_dir()

        # Callback que recibe el nombre tecleado por el usuario
        def on_modal_close(folder_name: str | None) -> None:
            if not folder_name:
                return  # Si canceló, no hacemos nada

            try:
                # Sanitizamos el nombre de entrada
                safe_name = self._sanitize_name(folder_name)
            except ValueError:
                self.notify("Nombre de carpeta inválido.", severity="error")
                return

            # Construimos la ruta de la nueva carpeta
            new_folder_path = base_dir / safe_name

            try:
                # Creamos el directorio. exist_ok=False lanzará error si ya existe
                os.makedirs(new_folder_path, exist_ok=False)
                self.notify(f"Carpeta creada: {safe_name}")
                self._refrescar_arbol()
            except FileExistsError:
                self.notify("Error: Ya existe una carpeta con ese nombre.", severity="error")
            except Exception as e:
                self.notify(f"Error al crear carpeta: {e}", severity="error")

        # Mostramos la ventana emergente para que ingrese el nombre de la carpeta
        self.push_screen(
            VentanaNombres("Nombre de la nueva carpeta: "),
            on_modal_close,
        )

    # Acción de crear archivo (tecla N)
    def action_create_file(self) -> None:
        base_dir = self._get_base_dir()

        # Callback cuando el usuario ingresa el nombre del archivo
        def on_modal_close(file_name: str | None) -> None:
            if not file_name:
                return

            try:
                # Sanitizamos el nombre contra inyecciones de ruta
                safe_name = self._sanitize_name(file_name)
            except ValueError:
                self.notify("Nombre de archivo inválido.", severity="error")
                return

            # Ruta de destino del nuevo archivo
            new_file_path = base_dir / safe_name

            try:
                # Nos aseguramos de crear directorios padres si hiciera falta
                new_file_path.parent.mkdir(parents=True, exist_ok=True)
                # Creamos el archivo vacío. exist_ok=False lanza error si ya existe
                new_file_path.touch(exist_ok=False)
                
                self.notify(f"Archivo creado: {safe_name}")
                self._refrescar_arbol()
            except FileExistsError:
                self.notify("Error: Ya existe un archivo con ese nombre.", severity="error")
            except Exception as e:
                self.notify(f"Error al crear archivo: {e}", severity="error")

        # Solicitamos el nombre del archivo
        self.push_screen(
            VentanaNombres("Nombre del nuevo archivo con su extensión: "),
            on_modal_close,
        )

    # Acción de copiar (tecla c)
    def action_copy(self) -> None:
        current_path = self._get_selected_path()

        if not current_path:
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        # Callback al obtener el destino de copia
        def on_modal_close(destination_input: str | None) -> None:
            if not destination_input:
                return

            # Resolvemos el destino
            target = self._resolve_path(destination_input)

            # Si es carpeta, copiamos el archivo manteniendo su nombre dentro de ella
            if target.is_dir() or destination_input.rstrip().endswith(("/", "\\")):
                new_path = target / current_path.name
            else:
                new_path = target

            # Validación de colisión
            if new_path.resolve() == current_path.resolve():
                self.notify("No se puede copiar un archivo sobre sí mismo.", severity="error")
                return

            # Validación de límites de seguridad
            try:
                new_path.relative_to(Path(".").resolve())
            except ValueError:
                self.notify("No se permite copiar fuera del directorio de trabajo.", severity="error")
                return

            try:
                new_path.parent.mkdir(parents=True, exist_ok=True)

                if current_path.is_file():
                    # Copiamos archivo físico manteniendo todos sus metadatos temporales y de permisos
                    shutil.copy2(current_path, new_path)
                elif current_path.is_dir():
                    if new_path.exists():
                        raise FileExistsError(f"Ya existe: {new_path}")
                    # Copiamos todo el directorio de forma totalmente recursiva
                    shutil.copytree(current_path, new_path)

                self.notify(f"Copiado con éxito a: {new_path}")
                self._refrescar_arbol()

            except FileExistsError:
                self.notify("Error: Ya existe un elemento en el destino.", severity="error")
            except Exception as e:
                self.notify(f"Error al copiar: {e}", severity="error")

        # Mostramos cuadro de texto para el destino del clon de archivo
        self.push_screen(
            VentanaNombres("Digite la carpeta destino del clon: "),
            on_modal_close,
        )

    # Acción de Visualizar Contenido de un archivo (tecla v)
    def action_view(self) -> None:
        current_path = self._get_selected_path()

        if not current_path:
            self.notify("No hay ningún archivo seleccionado", severity="warning")
            return

        if current_path.is_dir():
            self.notify("No se puede visualizar una carpeta", severity="warning")
            return

        # Para proteger el consumo de memoria de la app, establecemos un límite máximo de tamaño
        max_size = 5 * 1024 * 1024  # 5 Megabytes
        try:
            file_size = current_path.stat().st_size
            if file_size > max_size:
                self.notify(
                    f"Archivo demasiado grande ({file_size / 1024 / 1024:.1f} MB). Máximo permitido: 5 MB",
                    severity="warning",
                )
                return

            # Leemos los primeros 50,000 caracteres con decodificación UTF-8 robusta contra caracteres extraños
            with open(current_path, "r", encoding="utf-8", errors="replace") as f:
                contenido = f.read(50_000)

            # Abrimos la pantalla modal del visor de texto con la información cargada
            self.push_screen(VentanaVisualizador(current_path.name, contenido))

        except UnicodeDecodeError:
            self.notify("El archivo parece ser binario y no puede mostrarse.", severity="warning")
        except Exception as e:
            self.notify(f"No se pudo leer el archivo: {e}", severity="error")

    # Acción de Renombrar (tecla r)
    def action_rename(self) -> None:
        current_path = self._get_selected_path()

        if not current_path:
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        # Callback que recibe el nuevo nombre
        def on_modal_close(new_name: str | None) -> None:
            if not new_name:
                return

            try:
                # Sanitizamos la entrada del usuario
                safe_name = self._sanitize_name(new_name)
            except ValueError:
                self.notify("Nombre inválido.", severity="error")
                return

            # Creamos la nueva ruta en el mismo directorio pero con el nuevo nombre
            new_path = current_path.with_name(safe_name)

            # Verificamos si ya existe otra entidad con ese nombre en el mismo lugar
            if new_path.exists() and new_path.resolve() != current_path.resolve():
                self.notify("Error: Ya existe un archivo/carpeta con ese nombre", severity="error")
                return

            try:
                # Cambiamos el nombre en el sistema de archivos
                current_path.rename(new_path)
                self.notify(f"Renombrado a: {safe_name}")
                self._refrescar_arbol()
            except FileExistsError:
                self.notify("Error: Ya existe un archivo/carpeta con ese nombre", severity="error")
            except Exception as e:
                self.notify(f"Error al renombrar: {e}", severity="error")

        # Abrimos diálogo pidiendo el nuevo nombre
        self.push_screen(
            VentanaNombres("Nuevo nombre completo (con extensión si aplica): "),
            on_modal_close,
        )

    # Acción de Editar el archivo seleccionado (tecla e)
    def action_edit(self) -> None:
        current_path = self._get_selected_path()

        if not current_path:
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        if current_path.is_dir():
            self.notify("No se puede editar una carpeta.", severity="warning")
            return

        # Intentamos obtener el editor de texto configurado en la variable de entorno $EDITOR,
        # si no existe, usamos "vi" por defecto en plataformas UNIX/Linux
        editor = os.environ.get("EDITOR", "vi")

        # Editores interactivos de consola populares que se adueñan de la terminal
        terminal_editors = {"vi", "vim", "nvim", "nano", "emacs", "micro", "joe"}
        editor_name = os.path.basename(editor).lower()

        if editor_name in terminal_editors:
            # Para editores de terminal:
            # Dado que el editor interactivo y Textual compiten directamente por la renderización
            # de la pantalla de la terminal, debemos ceder el control.
            # El método 'self.suspend()' pausa temporalmente Textual, restaura la terminal a su
            # estado original nativo, y al retornar de la función (cuando el editor se cierra),
            # reanuda automáticamente la interfaz de Textual sin perder el estado de nuestra app.
            try:
                self.suspend()  # Detenemos Textual temporalmente
                # Usamos os.system para ejecutar de forma síncrona el editor de la consola
                os.system(f'{editor} "{current_path}"')
                self.notify(f"Archivo editado: {current_path.name}")
                self._refrescar_arbol()
            except Exception as e:
                self.notify(f"Error al abrir editor: {e}", severity="error")
        else:
            # Para editores gráficos (GUI) como VS Code, Sublime Text, Notepad++, etc.:
            # Al no adueñarse de la terminal de texto, no compiten por la pantalla.
            # Por ende, podemos ejecutarlos de fondo de forma no bloqueante usando nuestra helper.
            self._run_command_nonblocking(
                [editor, str(current_path)], f"Archivo abierto en {editor}"
            )

    # Acción de Abrir Externo (tecla o)
    def action_open_external(self) -> None:
        current_path = self._get_selected_path()

        if not current_path:
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        # Dependiendo del sistema operativo, ejecutamos el comando de apertura nativo predeterminado
        if sys.platform == "darwin":  # Para sistemas macOS
            self._run_command_nonblocking(
                ["open", str(current_path)], f"Abierto: {current_path.name}"
            )
        elif sys.platform == "win32":  # Para sistemas Windows
            try:
                # os.startfile es la API nativa de Windows que delega la apertura al SO de forma asíncrona
                os.startfile(str(current_path))
                self.notify(f"Abierto: {current_path.name}")
            except OSError as e:
                self.notify(f"No se pudo abrir: {e}", severity="error")
        else:  # Para distribuciones Linux y Unix compatibles
            # 'xdg-open' es el estándar en Linux para abrir archivos usando el gestor de ventanas del usuario.
            # Lo lanzamos de forma desvinculada para no congelar la UI si el programa externo tarda en arrancar.
            self._run_command_nonblocking(
                ["xdg-open", str(current_path)], f"Abierto: {current_path.name}"
            )

    # Acción de Ver Propiedades del archivo (tecla p)
    def action_properties(self) -> None:
        current_path = self._get_selected_path()

        if not current_path:
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        # Apilamos la pantalla de propiedades pasándole el Path del elemento
        self.push_screen(VentanaPropiedades(current_path))

    # Acción de Comprimir a archivo ZIP (tecla z)
    def action_zip_compress(self) -> None:
        current_path = self._get_selected_path()

        if not current_path:
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        # Definimos el nombre del ZIP por defecto
        zip_name = f"{current_path.name}.zip"
        zip_path = current_path.parent / zip_name

        # En caso de que ya exista un archivo .zip con el mismo nombre, agregamos un contador numérico
        counter = 1
        while zip_path.exists():
            zip_name = f"{current_path.name}_{counter}.zip"
            zip_path = current_path.parent / zip_name
            counter += 1

        try:
            # Abrimos el archivo zip en modo de escritura ('w')
            with ZipFile(zip_path, "w") as zf:
                if current_path.is_file():
                    # 1. Si es un archivo de datos simple, lo escribimos directamente dentro del ZIP
                    zf.write(current_path, current_path.name)
                else:
                    # 2. Si es una carpeta completa, barremos recursivamente usando rglob('*')
                    for file_path in current_path.rglob("*"):
                        if file_path.is_file():
                            # Usamos relative_to para que las rutas internas del ZIP sean relativas a la carpeta base.
                            # Esto previene que se empaqueten rutas de directorios padres innecesarias dentro del comprimido.
                            arcname = file_path.relative_to(current_path)
                            zf.write(file_path, arcname)

            self.notify(f"Comprimido: {zip_name}")
            self._refrescar_arbol()

        except Exception as e:
            self.notify(f"Error al comprimir: {e}", severity="error")

    # Acción de Extraer archivo ZIP (tecla Z)
    def action_zip_extract(self) -> None:
        current_path = self._get_selected_path()

        if not current_path:
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        # Validamos que sea un archivo con extensión .zip
        if current_path.suffix.lower() != ".zip":
            self.notify("El archivo seleccionado no es un .zip", severity="warning")
            return

        # El directorio destino de extracción tendrá el nombre del zip sin la extensión .zip
        extract_dir = current_path.with_suffix("")

        # Si ya existe un directorio con ese nombre en el disco, le agregamos un número secuencial
        counter = 1
        original_name = extract_dir.name
        while extract_dir.exists():
            extract_dir = current_path.parent / f"{original_name}_{counter}"
            counter += 1

        try:
            with ZipFile(current_path, "r") as zf:
                # --------------------------------------------------------------
                # VALIDACIÓN DE SEGURIDAD CRÍTICA CONTRA ATAQUES ZIP SLIP
                # --------------------------------------------------------------
                # Un archivo ZIP modificado maliciosamente puede contener rutas relativas
                # del tipo "../../../etc/cron" en el nombre de sus elementos, con la intención
                # de escribir archivos fuera del directorio de extracción asignado.
                for member in zf.namelist():
                    # Resolvemos la ruta de destino hipotética para este elemento interno
                    member_path = extract_dir / member
                    try:
                        # 'relative_to' valida de forma interna que 'member_path' comience con la ruta de 'extract_dir'.
                        # Si intenta escapar (ej: subiendo de nivel con ..), lanzará una excepción 'ValueError', deteniendo la extracción.
                        member_path.relative_to(extract_dir.resolve())
                    except ValueError:
                        raise ValueError(f"Archivo malicioso en zip detectado: {member}")

                # Una vez que confirmamos que todo el contenido es seguro, procedemos con la extracción total
                zf.extractall(extract_dir)

            self.notify(f"Extraído en: {extract_dir.name}")
            self._refrescar_arbol()

        except Exception as e:
            self.notify(f"Error al extraer: {e}", severity="error")

    # Acción de Copiar Ruta al portapapeles (tecla y)
    def action_copy_path(self) -> None:
        current_path = self._get_selected_path()

        if not current_path:
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        # Convertimos la ruta a su formato absoluto absoluto y limpio de string
        ruta = str(current_path.resolve())

        try:
            # Detectamos la plataforma para utilizar la utilidad de portapapeles correspondiente
            if sys.platform == "darwin":  # macOS
                subprocess.run(["pbcopy"], input=ruta, text=True, check=True)
            elif sys.platform == "win32":  # Windows
                subprocess.run(["clip"], input=ruta, text=True, check=True)
            else:  # Linux / Unix
                try:
                    # Intentamos usar xclip si el usuario está en un servidor X11
                    subprocess.run(
                        ["xclip", "-selection", "clipboard"],
                        input=ruta,
                        text=True,
                        check=True,
                    )
                except FileNotFoundError:
                    # Si no está xclip, intentamos wl-copy para sesiones de Wayland modernas
                    subprocess.run(["wl-copy"], input=ruta, text=True, check=True)

            self.notify(f"Ruta copiada: {ruta}")

        except Exception as e:
            # Si no hay herramientas de clipboard disponibles (típico en terminales puras SSH sin GUI),
            # mostramos la ruta en la barra de notificación emergente para que el usuario pueda copiarla manualmente de la consola.
            self.notify(
                f"Clipboard no disponible. Ruta: {ruta}\nError: {e}", severity="warning"
            )

    # Acción de Duplicar elemento (tecla d)
    def action_duplicate(self) -> None:
        current_path = self._get_selected_path()

        if not current_path:
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        # Creamos el nombre del clon agregando el sufijo " (copia)" antes de la extensión si es archivo
        if current_path.is_file():
            new_name = f"{current_path.stem} (copia){current_path.suffix}"
        else:
            new_name = f"{current_path.name} (copia)"

        new_path = current_path.parent / new_name

        # Si el clon ya existe en el disco, agregamos un contador secuencial numérico
        counter = 1
        while new_path.exists():
            if current_path.is_file():
                new_name = f"{current_path.stem} (copia {counter}){current_path.suffix}"
            else:
                new_name = f"{current_path.name} (copia {counter})"
            new_path = current_path.parent / new_name
            counter += 1

        try:
            # Duplicamos la entidad real según su tipo de nodo en el disco
            if current_path.is_file():
                shutil.copy2(current_path, new_path)
            else:
                shutil.copytree(current_path, new_path)

            self.notify(f"Duplicado: {new_name}")
            self._refrescar_arbol()

        except Exception as e:
            self.notify(f"Error al duplicar: {e}", severity="error")

    # Acción de Crear archivo con timestamp actual en su nombre (tecla t)
    def action_touch_timestamp(self) -> None:
        base_dir = self._get_base_dir()

        # Obtenemos la fecha y hora actual en un formato seguro y legible (ej: 2026-08-04_12-30-15)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"archivo_{timestamp}.txt"  # Creamos el nombre con extensión .txt

        new_file_path = base_dir / file_name

        try:
            # Creamos el archivo vacío mediante la llamada .touch() del módulo pathlib
            new_file_path.touch()
            self.notify(f"Archivo creado: {file_name}")
            self._refrescar_arbol()

        except Exception as e:
            self.notify(f"Error al crear archivo: {e}", severity="error")
