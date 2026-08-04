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
   styles.tcss — Styles for the File Manager (Textual)
   ============================================================ */

/* ---------- Main Screen ---------- */
Screen {
    background: #10141a;
    color: #d8dee9;
    layout: vertical;
}

Header {
    background: #1f2733;
    color: #88c0d0;
    text-style: bold;
    dock: top;
}

Footer {
    background: #1f2733;
    color: #d8dee9;
    dock: bottom;
}

Footer > .footer--key {
    color: #88c0d0;
    text-style: bold;
}

Footer > .footer--description {
    color: #a3b1c2;
}

/* ---------- Directory Tree ---------- */
DirectoryTree {
    background: #10141a;
    color: #d8dee9;
    border: round #2e3947;
    padding: 1 2;
    scrollbar-color: #3b4a5a;
    scrollbar-color-hover: #88c0d0;
    scrollbar-background: #10141a;
}

DirectoryTree:focus {
    border: round #88c0d0;
}

DirectoryTree > .directory-tree--folder {
    color: #ebcb8b;
    text-style: bold;
}

DirectoryTree > .directory-tree--file {
    color: #d8dee9;
}

DirectoryTree > .directory-tree--extension {
    color: #a3b1c2;
    text-style: italic;
}

DirectoryTree > .tree--cursor {
    background: #3b4a5a;
    color: #eceff4;
    text-style: bold;
}

DirectoryTree > .tree--highlight {
    background: #2e3947;
}

/* ============================================================
   Modals (ModalScreen) — semi-transparent background
   ============================================================ */
VentanaConfirmacion,
VentanaAyuda,
VentanaNombres {
    align: center middle;
    background: rgba(0, 0, 0, 0.6);
}

/* ---------- Confirmation / Rename / Move / etc. Dialog ---------- */
#modal_dialog {
    grid-size: 1 3;
    grid-gutter: 1 2;
    grid-rows: auto auto auto;
    padding: 1 3;
    width: 60;
    height: auto;
    max-height: 20;
    border: thick #88c0d0;
    background: #1b212b;
}

#modal_title {
    content-align: center middle;
    width: 100%;
    text-style: bold;
    color: #eceff4;
    background: #2e3947;
    padding: 0 1;
}

#modal_content {
    width: 100%;
    color: #d8dee9;
    padding: 1 0;
}

#confirm_input,
#folder_name {
    border: round #3b4a5a;
    background: #10141a;
    color: #eceff4;
    padding: 0 1;
}

#confirm_input:focus,
#folder_name:focus {
    border: round #88c0d0;
}

/* ---------- Help / File Viewer Window ---------- */
#help_dialog {
    grid-size: 1 2;
    grid-gutter: 1;
    grid-rows: auto 1fr;
    padding: 1 3;
    width: 80;
    height: 80%;
    border: thick #ebcb8b;
    background: #1b212b;
}

#help_title {
    content-align: center middle;
    width: 100%;
    text-style: bold;
    color: #1b212b;
    background: #ebcb8b;
    padding: 0 1;
}

#help_content {
    width: 100%;
    height: 1fr;
    color: #d8dee9;
    padding: 1 2;
    border: round #2e3947;
    overflow-y: auto;
}
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
