"""Wizard to create a new BIDS dataset"""

from tkinter import *
from tkinter import ttk

from .child_window import ChildWindow
from .pages import PAGES
from .wizard_state import WizardState


class NewDatasetWindow(ChildWindow):
    def __init__(self, parent: Tk) -> None:
        super().__init__(parent, "New dataset")
        self.wizard = WizardState()
        self._build_header()
        self._build_footer()
        self.pages = [page(self, self.wizard, self._show_error) for page in PAGES]
        self.current = 0
        self._show_page(0)

    def _build_header(self) -> None:
        self.step = ttk.Label(self, font=("TkDefaultFont", 14, "bold"), padding=(20, 20, 20, 0))
        self.step.pack(side=TOP, fill=X)

    def _build_footer(self) -> None:
        footer = ttk.Frame(self, padding=20)
        footer.pack(side=BOTTOM, fill=X)

        self.next_button = ttk.Button(footer, text="Next", command=self._next)
        self.next_button.pack(side=RIGHT, padx=(10, 0))
        self.previous_button = ttk.Button(footer, text="Previous", command=self._previous)

        ttk.Style(self).configure("Error.TLabel", foreground="red")
        self.error = ttk.Label(footer, style="Error.TLabel")
        self.error.pack(side=LEFT, fill=X, expand=True)
        self.error.bind("<Configure>", lambda event: self.error.configure(wraplength=event.width))

    def _show_error(self, message: str) -> None:
        self.error.configure(text=message)

    def _show_page(self, index: int) -> None:
        self.pages[self.current].pack_forget()
        self.current = index
        page = self.pages[index]
        page.on_show()
        page.pack(side=TOP, fill=BOTH, expand=True)
        self.step.configure(text=f"Step {index + 1} of {len(self.pages)} · {page.title}")
        self._show_error("")
        if index == 0:
            self.previous_button.pack_forget()
        else:
            self.previous_button.pack(side=RIGHT, padx=(10, 0), after=self.next_button)

    def _previous(self) -> None:
        self._show_page(self.current - 1)

    def _next(self) -> None:
        error = self.pages[self.current].check()
        if error:
            self._show_error(error)
            return
        if self.current < len(self.pages) - 1:
            self._show_page(self.current + 1)
