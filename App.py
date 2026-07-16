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

        ### definicion de acciones ###

    def action_help(self) -> None:  # ? -> menu de help
        self.notify("Le da ayuda... se va... epicamente")

    def action_delete(self) -> None:  # Del -> elimina
        self.notify("Se borra un arhivo... epicamente")

    def action_down(self) -> None:  # j -> baja
        tree = self.query_one(DirectoryTree)
        tree.action_cursor_down()

    def action_upp(self) -> None:  # k -> sube
        tree = self.query_one(DirectoryTree)
        tree.action_cursor_up()


if __name__ == "__main__":
    app = HolaMundo()
    app.run()
