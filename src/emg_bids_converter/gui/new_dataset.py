"""Window to create an empty BIDS dataset"""

from tkinter import *


class NewDatasetWindow(Toplevel):
    def __init__(self, parent: Tk) -> None:
        super().__init__(parent)
        self.title("New dataset")
        self._match_parent(parent)
        self.resizable(False, False)

    def _match_parent(self, parent: Tk) -> None:
        parent.update_idletasks()
        offset = int(parent.winfo_width() * 0.05)
        x = parent.winfo_x() + offset
        y = parent.winfo_y() + offset
        self.geometry(f"{parent.winfo_width()}x{parent.winfo_height()}+{x}+{y}")
