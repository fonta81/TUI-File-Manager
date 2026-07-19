# TUI File Manager

A lightweight, keyboard-driven Terminal User Interface (TUI) File Manager built with Python and [Textual](https://textual.textualize.io/). It allows you to navigate your directories and manage files directly from your terminal using modern modal popups and responsive shortcuts.

## Features

* **Interactive Directory Tree:** Browse folders and files dynamically with native auto-refresh.
* **Keyboard-Driven Workflow:** Quick operations using intuitive Vim-like and semantic shortcuts.
* **Smart Modals:** Built-in confirmation dialogs to prevent accidental loss when deleting non-empty directories.
* **Complete File Management:** Seamlessly create, delete, rename, move, and copy files or directories.
* **Contextual Notifications:** Real-time feedback for operations, warning popups, and error messages.

---

## Key Bindings & Shortcuts

Press `?` inside the application at any time to open the built-in Help Screen.

### Navigation
* `k` or `↑`: Scroll cursor up
* `j` or `↓`: Scroll cursor down

### File Operations
* `n`: Create a new folder
* `r`: Rename selected item
* `m`: Move file or folder to a target destination
* `c`: Copy (clone) file or folder recursively
* `Delete`: Delete selected file/folder (prompts for safety if a folder contains data)

### General
* `?`: Toggle help screen
* `q`: Quit the application
* `ESC`: Close active help or dialog windows

---

## Installation & Setup

1. **Prerequisites:** Ensure you have Python 3.8+ installed on your system.
2. **Install Dependencies:** This project relies on `textual`. Install it via pip:

```bash
pip install textual
