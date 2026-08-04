from pathlib import Path
from textual.widgets import DirectoryTree
from textual.widgets._tree import TreeNode
from rich.text import Text
from rich.console import RenderableType

class IconTree(DirectoryTree):
    def render_node(self, node: TreeNode) -> RenderableType:
        # Define some basic icons
        icon = "📄 "
        if node.data:
            path = node.data.path
            if path.is_dir():
                icon = "📁 "
            elif path.suffix == ".py":
                icon = "🐍 "
            elif path.suffix in (".css", ".tcss"):
                icon = "🎨 "
            elif path.suffix in (".md", ".txt"):
                icon = "📝 "
            elif path.suffix in (".zip", ".tar", ".gz"):
                icon = "📦 "
        
        label = Text(node.label)
        label.plain = icon + label.plain
        return label
