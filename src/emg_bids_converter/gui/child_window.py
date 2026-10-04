"""Base class of the secondary windows, opened over the main window"""

from tkinter import *


class ChildWindow(Toplevel):
    def __init__(self, parent: Tk, title: str) -> None:
        super().__init__(parent)
        self.title(title)
        self._match_parent(parent)
        self.resizable(False, False)

    def _match_parent(self, parent: Tk) -> None:
        parent.update_idletasks()
        offset = int(parent.winfo_width() * 0.05)
        x = parent.winfo_x() + offset
        y = parent.winfo_y() + offset
        self.geometry(f"{parent.winfo_width()}x{parent.winfo_height()}+{x}+{y}")
