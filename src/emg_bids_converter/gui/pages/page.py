"""Base class of the wizard pages"""

from collections.abc import Callable
from tkinter import *
from tkinter import ttk

from ..wizard_state import WizardState


class Page(ttk.Frame):
    title = ""

    def __init__(self, master: Misc, wizard: WizardState, show_error: Callable[[str], None]) -> None:
        super().__init__(master, padding=20)
        self.wizard = wizard
        self.show_error = show_error

    def on_show(self) -> None:
        """Called each time the page is displayed, to refresh it from what the previous pages collected"""

    def check(self) -> str | None:
        """Return an error message if the page does not allow going further, else None"""
        return None
