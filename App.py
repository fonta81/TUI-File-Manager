import os
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import DirectoryTree
from textual.binding import Binding
from textual.widgets import Footer
from textual.widgets import Header


class HolaMundo(App):
    BINDINGS = [
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
    ]

    def compose(self) -> ComposeResult:
        yield DirectoryTree("./")
        yield Footer()
        yield Header()

        ###### definicion de acciones ######

    def action_help(self) -> None:  # ? -> menu de help
        self.notify("Le da ayuda... se va... epicamente")

    def action_delete(self) -> None:  # Del -> elimina
        tree = self.query_one(DirectoryTree)

        node = tree.cursor_node

        if node is None or node.data is None:
            self.notify("No hay ningún archivo seleccionado.", severity="warning")
            return

        target_path: Path = node.data.path

        try:
            if target_path.is_file():
                os.remove(target_path)  # Borra el archivo
                self.notify(f"Archivo eliminado: {target_path.name}")
            elif target_path.is_dir():
                os.rmdir(target_path)
                self.notify(f"Carpeta eliminada: {target_path.name}")

            tree.reload()

        except Exception as e:
            self.notify(f"Error al eliminar: {e}", severity="error")

    def action_down(self) -> None:  # j -> baja
        tree = self.query_one(DirectoryTree)
        tree.action_cursor_down()

    def action_upp(self) -> None:  # k -> sube
        tree = self.query_one(DirectoryTree)
        tree.action_cursor_up()


if __name__ == "__main__":
    app = HolaMundo()
    app.run()
