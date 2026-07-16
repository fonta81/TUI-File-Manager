from textual.app import App, ComposeResult
from textual.widgets import DirectoryTree
from textual.binding import Binding
from textual.widgets import Footer


class DirectoryTreeApp(App):
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
        Binding(
            key="question_mark",
            action="help",
            description="Show help screen",
            key_display="?",
        ),
        Binding(key="d", action="delete", description="Delete the thing"),
        Binding(key="j", action="down", description="Scroll down", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield DirectoryTree("./")
        yield Footer()

        ### definicion de acciones ###

    def action_delete(self) -> None:
        self.notify("Hola Mundo ")


if __name__ == "__main__":
    app = DirectoryTreeApp()
    app.run()
