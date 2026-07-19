# Terminal File Manager (Administrador)

A lightweight, efficient, and interactive Terminal User Interface (TUI) file manager written in Python using the **Textual** framework. It allows you to quickly navigate your directory structure and perform essential file system operations completely within your terminal using keyboard shortcuts.

## Features

- **Directory Tree Navigation:** Seamlessly browse your files and folders.
- **File & Folder Operations:**
  - **Create Folders (`n`):** Create new subdirectories in the currently selected path.
  - **Rename (`r`):** Instantly rename files or folders.
  - **Move (`m`):** Move items securely to a specified target directory.
  - **Copy (`c`):** Recursively copy directories or duplicate single files safely.
  - **Delete (`Delete`):** Remove files directly or safely delete folders (with interactive confirmation dialogs for non-empty folders).
- **File Viewer (`v`):** View the first 50,000 characters of text-based files instantly in an overlaid modal without leaving the app.
- **Interactive Modals:** Beautifully centered dialog prompts for confirmations, names, and errors.
- **Built-in Help Overlay (`?`):** Access the quick-reference keyboard guide anytime.

---

## Keyboard Shortcuts

| Key | Action | Description |
| :---: | :--- | :--- |
| `k` / `↑` | **Scroll Up** | Move the cursor up the directory tree |
| `j` / `↓` | **Scroll Down** | Move the cursor down the directory tree |
| `n` | **New Folder** | Create a new folder at the current location |
| `r` | **Rename** | Rename the selected file or folder |
| `m` | **Move** | Move the selected item to a target path |
| `c` | **Copy** | Copy the selected item to a target path |
| `v` | **View** | Preview text file contents in a modal |
| `Delete` | **Delete** | Delete the selected file or directory |
| `?` | **Help** | Toggle the help screen guide |
| `q` | **Quit** | Exit the application |

---

## Prerequisites

Make sure you have Python 3.8+ and the `textual` package installed.

```bash
pip install textual
```

## Running the Application

1. Save the code into a file named `App.py`.
2. Launch it from your terminal:

```bash
python App.py
```

## Structure

The file consists of:
- `Administrador`: The core application class managing state, layouts, key bindings, and main file actions.
- `VentanaAyuda`: Modal menu detailing keyboard actions.
- `VentanaNombres`: Dynamic input modal for paths and text collection.
- `VentanaConfirmacion`: Protection modal ensuring you do not accidentally remove non-empty folders without entering confirmation (`S` or `si`).
