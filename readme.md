# Textual Terminal File Manager

A lightweight, keyboard-driven Terminal User Interface (TUI) file manager built in Python using the [Textual](https://textual.textualize.io/) framework.

---

## Features

- **Interactive Directory Tree:** Easily navigate your file system with quick keyboard shortcuts.
- **File & Directory Management:** Create, rename, move, copy, and delete files or folders directly from the terminal.
- **Safe Directory Deletion:** Prompts a confirmation modal before recursively deleting non-empty folders.
- **Quick File Preview:** Read text file contents up to 50,000 characters in a popup viewer.
- **Built-in Help System:** View available keybindings anytime by pressing `?`.
- **Cross-Platform Clipboard Support:** Copy file paths to the system clipboard using `xclip`, `wl-copy`, `pbcopy`, or `clip`.
- **Zip Compression & Extraction:** Compress files or folders to `.zip` and extract `.zip` archives safely (with Zip Slip protection).
- **External Editor Integration:** Open files in your preferred `$EDITOR` (supports both terminal and GUI editors).
- **File Properties Viewer:** Inspect file size, permissions, modification dates, and more.
- **Custom Dark Theme:** Fully styled with a custom `styles.tcss` using a Nord-inspired color palette.

---

## Requirements

- Python 3.8+
- [Textual](https://pypi.org/project/textual/) library

---

## Installation

1. **Clone or download** this repository.
2. **Install dependencies:**
   ```bash
   pip install textual
   ```

---

## Usage

Run the main application file from your terminal:

```bash
python main.py
```

> **Note:** The application looks for a custom stylesheet named `styles.tcss` in the same directory for custom styling (modals, dialogs, colors).

---

## Keybindings & Navigation

| Key | Action | Description |
| :--- | :--- | :--- |
| `k` / `↑` | Scroll Up | Move cursor up in the directory tree |
| `j` / `↓` | Scroll Down | Move cursor down in the directory tree |
| `n` | New Folder | Create a new directory |
| `N` | New File | Create a new file (including extension) |
| `r` | Rename | Rename selected file or folder |
| `m` | Move | Move selected item to a target path |
| `c` | Copy | Copy selected file/folder to a destination |
| `v` | View | Preview text content of the selected file |
| `e` | Edit | Open file in `$EDITOR` |
| `o` | Open External | Open file with the system's default application |
| `p` | Properties | Show detailed file properties |
| `z` | Compress | Compress selected file/folder to `.zip` |
| `Z` | Extract | Extract a `.zip` archive |
| `y` | Copy Path | Copy the absolute file path to clipboard |
| `d` | Duplicate | Create a duplicate of the selected file/folder |
| `t` | Touch Timestamp | Create an empty file with a timestamp name |
| `Delete` | Delete | Delete selected file or directory |
| `F5` | Refresh | Reload file tree |
| `?` | Help | Open help menu |
| `q` | Quit | Exit the application |

---

## Stylesheet (`styles.tcss`)

The application uses a custom Textual CSS (`styles.tcss`) file for a polished, dark-themed UI. Place this file in the same directory as `App.py`.

```tcss
/* ============================================================
   styles.tcss — Estilos para el Administrador de Archivos (Textual)
   ============================================================ */

/* ---------- Pantalla principal ---------- */
Screen {
    background: #2e3440; /* Nord0 (Darker) */
    color: #d8dee9;      /* Nord4 */
    layout: vertical;
}

Header {
    background: #3b4252; /* Nord1 */
    color: #88c0d0;      /* Nord8 */
    text-style: bold;
    dock: top;
    padding: 0 1;
}

Footer {
    background: #3b4252; /* Nord1 */
    color: #d8dee9;      /* Nord4 */
    dock: bottom;
    padding: 0 1;
}

Footer > .footer--key {
    color: #81a1c1;      /* Nord9 */
    text-style: bold;
}

Footer > .footer--description {
    color: #a3b1c2;      /* Nord5 */
}

/* ---------- Árbol de directorios ---------- */
DirectoryTree {
    background: #2e3440; /* Nord0 */
    color: #d8dee9;      /* Nord4 */
    border: none;
    padding: 1 2;
    scrollbar-color: #434c5e; /* Nord2 */
    scrollbar-color-hover: #88c0d0; /* Nord8 */
    scrollbar-background: #2e3440; /* Nord0 */
}

DirectoryTree:focus {
    border: none;
}

DirectoryTree > .directory-tree--folder {
    color: #ebcb8b; /* Nord13 */
    text-style: bold;
}

DirectoryTree > .directory-tree--file {
    color: #eceff4; /* Nord6 */
}

DirectoryTree > .directory-tree--extension {
    color: #5e81ac; /* Nord10 */
    text-style: italic;
}

DirectoryTree > .tree--cursor {
    background: #434c5e; /* Nord2 */
    color: #ffffff;
    text-style: bold;
}

DirectoryTree > .tree--highlight {
    background: #3b4252; /* Nord1 */
}

/* ============================================================
   Modales (ModalScreen) — fondo semitransparente
   ============================================================ */
VentanaConfirmacion,
VentanaAyuda,
VentanaNombres {
    align: center middle;
    background: rgba(46, 52, 64, 0.8);
}

/* ---------- Dialogo de confirmación / renombrar / mover / etc. ---------- */
#modal_dialog {
    grid-size: 1 3;
    grid-gutter: 1 2;
    grid-rows: auto auto auto;
    padding: 2 4;
    width: 60;
    height: auto;
    max-height: 20;
    border: thick #88c0d0; /* Nord8 */
    background: #3b4252; /* Nord1 */
}

#modal_title {
    content-align: center middle;
    width: 100%;
    text-style: bold;
    color: #2e3440; /* Nord0 */
    background: #88c0d0; /* Nord8 */
    padding: 0 1;
}

#modal_content {
    width: 100%;
    color: #d8dee9; /* Nord4 */
    padding: 1 0;
}

#confirm_input,
#folder_name {
    border: round #434c5e; /* Nord2 */
    background: #2e3440; /* Nord0 */
    color: #eceff4; /* Nord6 */
    padding: 0 1;
}

#confirm_input:focus,
#folder_name:focus {
    border: round #88c0d0; /* Nord8 */
}

/* ---------- Status bar ---------- */
#status_bar {
    background: #434c5e; /* Nord2 */
    color: #eceff4;      /* Nord6 */
    padding: 0 1;
    dock: bottom;
}

/* ---------- Ventana de ayuda / visor de archivo ---------- */
#help_dialog {
    grid-size: 1 2;
    grid-gutter: 1;
    grid-rows: auto 1fr;
    padding: 2 4;
    width: 80;
    height: 80%;
    border: thick #ebcb8b; /* Nord13 */
    background: #3b4252; /* Nord1 */
}

#help_title {
    content-align: center middle;
    width: 100%;
    text-style: bold;
    color: #2e3440; /* Nord0 */
    background: #ebcb8b; /* Nord13 */
    padding: 0 1;
}

#help_content {
    width: 100%;
    height: 1fr;
    color: #d8dee9; /* Nord4 */
    padding: 1 2;
    border: none;
    overflow-y: auto;
}
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
