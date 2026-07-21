# Textual Terminal File Manager

A lightweight, keyboard-driven Terminal User Interface (TUI) file manager built in Python using the [Textual](https://textual.textualize.io/) framework.

---

## Features

- **Interactive Directory Tree:** Easily navigate your file system with quick keyboard shortcuts.
- **File & Directory Management:** Create, rename, move, copy, and delete files or folders directly from the terminal.
- **Safe Directory Deletion:** Prompts a confirmation modal before recursively deleting non-empty folders.
- **Quick File Preview:** Read text file contents up to 50,000 characters in a popup viewer.
- **Built-in Help System:** View available keybindings anytime by pressing `?`.

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
python App.py
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
| `Delete` | Delete | Delete selected file or directory |
| `F5` | Refresh | Reload file tree |
| `?` | Help | Open help menu |
| `q` | Quit | Exit the application |

- This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details