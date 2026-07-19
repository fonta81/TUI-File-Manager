# se importan las librerias a usar:
import os
from pathlib import Path
import shutil

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, Footer, Header, Input, Label, Static


class VentanaConfirmacion(ModalScreen[bool]):  # Retorna True o False
    def __init__(self, mensaje: str, **kwargs):
        super().__init__(**kwargs)
        self.mensaje = mensaje

    def compose(self) -> ComposeResult:  # mostramos el mensaje:
        texto_instrucciones = f"{self.mensaje}\n\n[dim]Escribe [b]S[/b] para confirmar o cualquier otra cosa para cancelar.[/]"
        yield Grid(
            Label("CONFIRMACIÓN", id="modal_title"),
            Input(placeholder="¿Confirmar? (S/N): ", id="confirm_input"),
            Static(texto_instrucciones, id="modal_content"),
            id="modal_dialog",
        )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # Si el usuario escribe 's' o 'si', confirmamos (True)
        if event.value.strip().lower() in ["s", "si"]:
            self.dismiss(True)
        else:
            self.dismiss(False)


class VentanaAyuda(ModalScreen):  # ventana help
    # Atajos para cerrar la ayuda rápidamente con Esc, ? o q
    BINDINGS = [Binding("escape,?,q", "dismiss", "Cerrar Ayuda")]

    def compose(self) -> ComposeResult:  # ayuda:
        texto_ayuda = (
            "[bold]Guía de Atajos de Teclado[/]\n\n"
            "[substantive]Navegación:[/]\n"
            "  [b]k[/] o [b]↑[/]     - Subir en el árbol\n"
            "  [b]j[/] o [b]↓[/]     - Bajar en el árbol\n\n"
            "[substantive]Acciones:[/]\n"
            "  [b]n[/]         - Crear una nueva carpeta\n"
            "  [b]r[/]         - Renombrar archivo o carpeta\n"
            "  [b]m[/]         - Mover archivo o carpeta\n"
            "  [b]c[/]    - Copiar elemento seleccionado\n\n"
            "  [b]v[/]    - Ver contenido de un archivo de texto\n\n"
            "  [b]Delete[/]    - Eliminar elemento seleccionado\n\n"
            "[substantive]General:[/]\n"
            "  [b]?[/]         - Mostrar/Ocultar esta ayuda\n"
            "  [b]q[/]         - Salir de la aplicación\n\n"
            "[dim]Presiona cualquier tecla asignada o ESC para cerrar[/]"
        )

        yield Grid(
            Label("AYUDA", id="help_title"),
            Static(texto_ayuda, id="help_content"),
            id="help_dialog",
        )


class VentanaNombres(ModalScreen[str]):  # ventana que pedira nombres,ect...
    def __init__(self, placeholder_text: str = "Nombre: ", **kwargs):
        super().__init__(**kwargs)
        self.placeholder_text = placeholder_text

    def compose(self) -> ComposeResult:
        yield Grid(  # pide el nombre al usuario -> lo guarda en la id
            Input(placeholder=self.placeholder_text, id="folder_name"),
            id="modal_dialog",
        )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value.strip():  # Quita espacios:
            self.dismiss(event.value.strip())  # cierra ventana y regresa valores
        else:
            self.dismiss(None)  # cierra ventana y regresa none


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
        Binding(key="k", action="upp", description="Scroll up", show=False),
        Binding(key="n", action="create_folder", description="New Folder"),
        Binding(key="r", action="rename", description="Rename"),
        Binding(key="m", action="move", description="move"),
        Binding(key="c", action="copy", description="copy"),
        Binding(key="v", action="view", description="View file content"),
    ]

    def compose(self) -> ComposeResult:  # lo que se "Imprimira" en la terminal:
        yield DirectoryTree("./")
        yield Footer()
        yield Header()

        # definimos las acciones que se habian asignado en el bindings:
        ###### definicion de acciones ######

    def action_down(self) -> None:  # j -> baja
        tree = self.query_one(DirectoryTree)  # cual es el path del cursor
        tree.action_cursor_down()  # baja el cursor una vez

    def action_upp(self) -> None:  # k -> sube
        tree = self.query_one(DirectoryTree)  # cual es el path del cursor
        tree.action_cursor_up()  # sube el cursor una vez

    def action_help(self) -> None:  # ? -> menu de help
        self.push_screen(VentanaAyuda())

    def action_delete(self) -> None:  # Del -> elimina
        tree = self.query_one(DirectoryTree)  # guarda la ruta actual
        node = tree.cursor_node  # guarda la ruta del cursor

        if node is None or node.data is None:  # no hay nada -> se sale de la funcion
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        target_path: Path = node.data.path  # guarda el path del archivo a eliminar

        try:
            if target_path.is_file():  # si es archivo
                os.remove(target_path)  # Borra el archivo
                self.notify(f"Archivo eliminado: {target_path.name}")
                self.refrescar_arbol(tree)
            elif target_path.is_dir():  # si es Carpeta
                try:
                    os.rmdir(target_path)  # Intenta borrarla si está vacía
                    self.notify(f"Carpeta vacía eliminada: {target_path.name}")
                    self.refrescar_arbol(tree)

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
                                self.refrescar_arbol(tree)
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
                            f"La carpeta '{target_path.name}' contiene información."
                        ),
                        procesar_confirmacion,
                    )

        except Exception as e:  # en caso de otro tipo de error:
            self.notify(f"Error al eliminar: {e}", severity="error")

    def action_move(self) -> None:  # m -> Mover archivo o carpeta
        tree = self.query_one(DirectoryTree)
        node = tree.cursor_node

        # 1. Validación: Verificar si hay algo seleccionado
        if node is None or node.data is None:
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        current_path: Path = node.data.path

        # 2. Callback que se ejecuta cuando el usuario escribe el destino en el Modal
        def on_modal_close(destination_input: str | None) -> None:
            if not destination_input:
                return  # Si cancela o está vacío, no hace nada

            # Convertimos la entrada del usuario en un objeto Path
            target_dir = Path(destination_input.strip())

            # Si el usuario da una ruta de carpeta, mantenemos el nombre original del archivo
            if target_dir.is_dir() or destination_input.endswith("/"):
                new_path = target_dir / current_path.name
            else:
                new_path = target_dir

            try:
                # Aseguramos que las carpetas del destino existan antes de mover
                new_path.parent.mkdir(parents=True, exist_ok=True)

                # Movemos el archivo o directorio
                current_path.rename(new_path)

                self.notify(f"Movido con éxito a: {new_path}")
                self.refrescar_arbol(tree)

            except FileExistsError:  # en caso de que ya exista:
                self.notify(
                    "Error: Ya existe un archivo en el destino.", severity="error"
                )
            except Exception as e:  # en caso de otro error:
                self.notify(f"Error al mover: {e}", severity="error")

        # 3. Abrimos el modal. Reutilizamos CreateFolderModal pero podemos cambiar visualmente el placeholder si fuese necesario.
        self.push_screen(VentanaNombres("Digite la carpeta destino: "), on_modal_close)

    def action_create_folder(self) -> None:  # n -> makedir
        tree = self.query_one(DirectoryTree)  # Ruta de donde se encuentra el .py

        node = tree.cursor_node  # Ruta del cursor
        if node is not None and node.data is not None:  # Hay algo seleccionado?:
            current_path: Path = node.data.path  # guarda el path
            # El path es de un archivo o de una capreta:
            base_dir = current_path.parent if current_path.is_file() else current_path
        else:  # seleccion == none -> creara la carpeta en la raiz:
            base_dir = Path("./")

        def on_modal_close(folder_name: str | None) -> None:
            if not folder_name:  # si no dijito el nombre:
                return  # salir

            new_folder_path = base_dir / folder_name  # crea la ruta de la carpeta nueva

            try:
                os.makedirs(new_folder_path, exist_ok=False)  # crea la carpeta
                self.notify(f"Carpeta creada: {folder_name}")  # mensaje

                self.refrescar_arbol(tree)
            except FileExistsError:  # si el archivo existe:
                self.notify(
                    "Error: Ya existe una carpeta con ese nombre.", severity="error"
                )
            except Exception as e:  # Cualquier otro error:
                self.notify(f"Error al crear carpeta: {e}", severity="error")

        # le mostramos la ventada de input y le damos el mensaje que mostramos:
        self.push_screen(
            VentanaNombres("Nombre de la nueva carpeta: "),
            on_modal_close,
        )

    def action_copy(self) -> None:  # c -> Copiar archivo o carpeta
        tree = self.query_one(DirectoryTree)
        node = tree.cursor_node

        # 1. Validación: Verificar si hay algo seleccionado
        if node is None or node.data is None:
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        current_path: Path = node.data.path

        # 2. Callback cuando el usuario ingresa el destino en el Modal
        def on_modal_close(destination_input: str | None) -> None:
            if not destination_input:
                return  # Si cancela, no hace nada

            target_dir = Path(destination_input.strip())

            # Si el destino es una carpeta existente o termina en "/", mantenemos el nombre original
            if target_dir.is_dir() or destination_input.endswith("/"):
                new_path = target_dir / current_path.name
            else:
                new_path = target_dir

            try:
                # Aseguramos que las carpetas del destino existan
                new_path.parent.mkdir(parents=True, exist_ok=True)

                # 3. Realizar la copia dependiendo de si es archivo o directorio
                if current_path.is_file():
                    shutil.copy2(
                        current_path, new_path
                    )  # Copia archivo manteniendo metadatos
                elif current_path.is_dir():
                    shutil.copytree(
                        current_path, new_path
                    )  # Copia carpetas de forma recursiva

                self.notify(f"Copiado con éxito a: {new_path}")
                self.refrescar_arbol(tree)

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
        tree = self.query_one(DirectoryTree)  # ver directorio del archivo
        node = tree.cursor_node  # ver directorio del puntero

        if node is None or node.data is None:  # Si no hay nada seleccionado
            self.notify("No hay ningun archivo seleccionado", severity="warning")
            return

        current_path: Path = node.data.path

        if current_path.is_dir():  # si es una carpeta
            self.notify("No se puede visualisar una carpeta", severity="warning")
            return

        try:  # abrimos el archivo en read y vemos los primeros 50k de caracteres
            with open(current_path, "r", encoding="utf-8", errors="replace") as f:
                contenido = f.read(50_000)

            class VentanaVisualizador(ModalScreen):
                BINDINGS = [Binding("escape,q,v", "dismiss", "cerrar")]

                def compose(self) -> ComposeResult:
                    yield Grid(
                        Label(f"Contenido de: {current_path.name}", id="help_title"),
                        Static(contenido, id="help_content", expand=True),
                        id="help_dialog",
                    )

            self.push_screen(VentanaVisualizador())

        except Exception as e:
            self.notify(f"No se pudo leer el archivo: {e}", severity="error")

    def action_rename(self) -> None:  # r -> Rename
        # rutas:
        tree = self.query_one(DirectoryTree)  # guarda la ruta actual
        node = tree.cursor_node  # guarda la ruta del cursor
        # en caso este vacio:
        if node is None or node.data is None:  # no hay nada -> se sale de la funcion
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return
        # el path actual:
        current_path: Path = node.data.path

        # acceda a la ventana de rename:
        def on_modal_close(folder_name: str | None) -> None:
            if not folder_name:  # en caso de que este vacio
                return  # salir

            # ruta del archivo con el nombre remplazado
            New_path = current_path.with_stem(folder_name)

            try:  # el codgio que cambia el nombre:
                current_path.rename(New_path)
                self.notify("Se renombro correctamente")  # mensaje
                self.refrescar_arbol(tree)

            except FileExistsError:  # si el archivo existe:
                self.notify(
                    "Error: ya existe un archivo/carpeta con ese nombre",
                    severity="error",
                )
            except Exception as e:  # Cualquier otro error:
                self.notify(f"Error al crear carpeta: {e}", severity="error")

        # abre la ventana de input y le damos el mensaje que mostrara:
        self.push_screen(VentanaNombres("Digite el nuevo nombre: "), on_modal_close)

    def refrescar_arbol(self, tree: DirectoryTree) -> None:  # Fuerza refresco
        node = tree.cursor_node
        if node and node.parent:
            tree.reload_node(node.parent)
        else:
            tree.reload()


if __name__ == "__main__":
    app = Administrador()
    app.run()
