# se importan las librerias a usar:
import os
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import DirectoryTree
from textual.binding import Binding
from textual.widgets import Footer
from textual.widgets import Header
from textual.screen import ModalScreen
from textual.widgets import Input
from textual.containers import Grid


class CreateFolderModal(ModalScreen[str]):
    def compose(self) -> ComposeResult:
        yield Grid(
            Input(placeholder="Nombre de la nueva carpeta...", id="folder_name"),
            id="modal_dialog",
        )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value.strip():
            self.dismiss(event.value.strip())
        else:
            self.dismiss(None)


class HolaMundo(App):  # iniciamos la app
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
        self.notify("Le da ayuda... se va... epicamente")

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
            elif target_path.is_dir():  # si es Carpeta
                os.rmdir(target_path)  # Borra la Carpeta
                self.notify(f"Carpeta eliminada: {target_path.name}")

            tree.reload()  # refresca el menu

        except Exception as e:  # en caso de error:
            self.notify(f"Error al eliminar: {e}", severity="error")

    def action_create_folder(self) -> None:
        tree = self.query_one(DirectoryTree)

        node = tree.cursor_node
        if node is not None and node.data is not None:
            current_path: Path = node.data.path
            base_dir = current_path.parent if current_path.is_file() else current_path
        else:
            base_dir = Path("./")

        def on_modal_close(folder_name: str | None) -> None:
            if not folder_name:
                return

            new_folder_path = base_dir / folder_name

            try:
                os.makedirs(new_folder_path, exist_ok=False)
                self.notify(f"Carpeta creada: {folder_name}")

                tree.reload()
            except FileExistsError:
                self.notify(
                    "Error: Ya existe una carpeta con ese nombre.", severity="error"
                )
            except Exception as e:
                self.notify(f"Error al crear carpeta: {e}", severity="error")

        self.push_screen(CreateFolderModal(), on_modal_close)


if __name__ == "__main__":
    app = HolaMundo()
    app.run()
