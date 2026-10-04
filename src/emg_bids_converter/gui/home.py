"""Main window of the graphical interface"""

from importlib.metadata import version
from tkinter import *
from tkinter import ttk

from ..api import PACKAGE


class Home(Tk):
    """Main window: entry point to create a dataset or add a recording"""

    def __init__(self) -> None:
        super().__init__()
        self.title("EMG-BIDS Converter")
        self._center_square()
        self.resizable(False, False)
        self._build_header()

    def _center_square(self) -> None:
        """Size the window as a square of half the screen height, centered on the screen"""
        side = int(self.winfo_screenheight() / 2)
        x = int((self.winfo_screenwidth() - side) / 2)
        y = int((self.winfo_screenheight() - side) / 2)
        self.geometry(f"{side}x{side}+{x}+{y}")

    def _build_header(self) -> None:
        """Title, subtitle and copyright line at the top of the window"""
        header = ttk.Frame(self, padding=20)
        header.pack(side=TOP, fill=X)

        ttk.Label(header, text="EMG-BIDS Converter", font=("TkDefaultFont", 24, "bold")).pack()
        ttk.Label(header, text="Convert EMG recordings to the BIDS standard").pack(pady=(4, 0))
        ttk.Label(header, text=f"© 2026 Hugo Haffad · MIT License · v{version(PACKAGE)}",
                  font=("TkDefaultFont", 10)).pack(pady=(8, 0))
