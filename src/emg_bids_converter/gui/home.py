"""Main window of the GUI"""

from importlib.metadata import version
from tkinter import *
from tkinter import ttk

from ..api import PACKAGE


class Home(Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("EMG-BIDS Converter")
        self._center_square()
        self.resizable(False, False)
        self._build_header()
        self._build_actions()

    def _center_square(self) -> None:
        side = int(self.winfo_screenheight() / 2)
        x = int((self.winfo_screenwidth() - side) / 2)
        y = int((self.winfo_screenheight() - side) / 2)
        self.geometry(f"{side}x{side}+{x}+{y}")

    def _build_header(self) -> None:
        header = ttk.Frame(self, padding=20)
        header.pack(side=TOP, fill=X)

        ttk.Label(header, text="EMG-BIDS Converter", font=("TkDefaultFont", 24, "bold")).pack()
        ttk.Label(header, text="Convert EMG recordings to the BIDS standard").pack(pady=(4, 0))
        ttk.Label(header, text=f"© 2026 Hugo Haffad · MIT License · v{version(PACKAGE)}",
                  font=("TkDefaultFont", 10)).pack(pady=(8, 0))

    def _build_actions(self) -> None:
        actions = ttk.Frame(self, padding=20)
        actions.pack(side=TOP, fill=BOTH, expand=True)
        actions.columnconfigure((0, 1), weight=1, uniform="action")
        actions.rowconfigure(0, weight=1)

        ttk.Button(actions, text="New dataset").grid(row=0, column=0, sticky=EW, padx=10)
        ttk.Button(actions, text="Add recording").grid(row=0, column=1, sticky=EW, padx=10)
