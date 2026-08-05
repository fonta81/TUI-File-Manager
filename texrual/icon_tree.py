# ==============================================================================
# COMPONENTE DE ÁRBOL DE DIRECTORIOS CON ICONOS (IconTree)
# ==============================================================================
# Este módulo personaliza el widget DirectoryTree estándar de Textual.
# Su objetivo es renderizar cada nodo (carpeta o archivo) anteponiéndole un emoji
# que represente visualmente su tipo o extensión de archivo.

from pathlib import Path
from textual.widgets import DirectoryTree
from textual.widgets._tree import TreeNode
from rich.text import Text
from rich.console import RenderableType

# Heredamos de 'DirectoryTree' para reutilizar toda su lógica de navegación,
# lectura del sistema de archivos y gestión de carpetas del framework Textual.
class IconTree(DirectoryTree):
    
    # Sobreescribimos el método 'render_node' que Textual llama para dibujar
    # cada elemento (nodo) del árbol en la terminal.
    def render_node(self, node: TreeNode) -> RenderableType:
        # 1. Definimos un icono por defecto (para archivos genéricos o desconocidos)
        icon = "📄 "
        
        # 2. Verificamos si el nodo tiene datos asociados (generalmente información del archivo)
        if node.data:
            # Obtenemos el objeto Path de la ruta correspondiente a este nodo
            path = node.data.path
            
            # 3. Determinamos el icono adecuado según el tipo de elemento en el sistema de archivos:
            if path.is_dir():
                # Si es un directorio/carpeta, le ponemos un emoji de carpeta
                icon = "📁 "
            elif path.suffix == ".py":
                # Si es un archivo de Python, usamos una serpiente
                icon = "🐍 "
            elif path.suffix in (".css", ".tcss"):
                # Si es una hoja de estilos (CSS o TCSS de Textual), usamos una paleta de pintura
                icon = "🎨 "
            elif path.suffix in (".md", ".txt"):
                # Si es un archivo de Markdown o de texto plano, usamos una nota/cuaderno
                icon = "📝 "
            elif path.suffix in (".zip", ".tar", ".gz"):
                # Si es un archivo comprimido o empaquetado, usamos una caja/paquete
                icon = "📦 "
        
        # 4. Obtenemos el texto de la etiqueta original del nodo (el nombre del archivo/carpeta)
        label = Text(node.label)
        
        # 5. Modificamos el texto plano anteponiéndole el icono seleccionado al nombre original.
        # Esto cambia la representación visual sin alterar la ruta real asociada al nodo.
        label.plain = icon + label.plain
        
        # Retornamos el objeto Text que contiene el nombre formateado para que sea renderizado
        return label
