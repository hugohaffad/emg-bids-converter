"""Main window of the graphical interface"""

from tkinter import *


class Home(Tk):
    """Main window: entry point to create a dataset or add a recording"""

    def __init__(self) -> None:
        super().__init__()
        self.title("EMG-BIDS Converter")
        self._center_square()
        self.resizable(False, False)

    def _center_square(self) -> None:
        """Size the window as a square of half the screen height, centered on the screen"""
        side = int(self.winfo_screenheight() / 2)
        x = int((self.winfo_screenwidth() - side) / 2)
        y = int((self.winfo_screenheight() - side) / 2)
        self.geometry(f"{side}x{side}+{x}+{y}")
