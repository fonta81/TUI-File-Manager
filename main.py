# ==============================================================================
# PUNTO DE ENTRADA PRINCIPAL DE LA APLICACIÓN
# ==============================================================================
# Este archivo es el punto de inicio para ejecutar nuestro gestor de archivos.
# Se encarga de inicializar y arrancar la aplicación de consola (TUI).

# Importamos la clase principal 'Administrador' desde el paquete 'texrual'
from texrual import Administrador

# Verificamos si este archivo se está ejecutando directamente desde la consola
if __name__ == "__main__":
    # Creamos una instancia de nuestra aplicación
    app = Administrador()
    
    # Arrancamos la aplicación llamando a su método 'run' (heredado de textual.app.App)
    app.run()
