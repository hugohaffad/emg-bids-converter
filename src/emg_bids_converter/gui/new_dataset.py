"""Wizard to create a new BIDS dataset"""

from tkinter import *
from tkinter import filedialog, ttk

from .child_window import ChildWindow


class NewDatasetWindow(ChildWindow):
    def __init__(self, parent: Tk) -> None:
        super().__init__(parent, "New dataset")
        self._build_form()
        self._build_footer()

    def _build_form(self) -> None:
        form = ttk.Frame(self, padding=20)
        form.pack(side=TOP, fill=X)
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Dataset name *").grid(row=0, column=0, sticky=W, padx=(0, 10))
        self.name = StringVar()
        self.name_entry = ttk.Entry(form, textvariable=self.name)
        self.name_entry.grid(row=0, column=1, columnspan=2, sticky=EW)
        self.name_entry.focus_set()

        ttk.Label(form, text="Dataset folder *").grid(row=1, column=0, sticky=W, padx=(0, 10), pady=(10, 0))
        self.folder = StringVar()
        self.folder_entry = ttk.Entry(form, textvariable=self.folder)
        self.folder_entry.grid(row=1, column=1, sticky=EW, pady=(10, 0))
        ttk.Button(form, text="Browse…", command=self._browse_folder).grid(row=1, column=2, padx=(10, 0), pady=(10, 0))

        ttk.Label(form, text="Authors").grid(row=2, column=0, sticky=W, padx=(0, 10), pady=(10, 0))
        self.author = StringVar()
        self.author_entry = ttk.Entry(form, textvariable=self.author)
        self.author_entry.grid(row=2, column=1, sticky=EW, pady=(10, 0))
        self.author_entry.bind("<Return>", lambda event: self._add_author())
        ttk.Button(form, text="Add", command=self._add_author).grid(row=2, column=2, sticky=EW, padx=(10, 0), pady=(10, 0))

        self.authors_list = Listbox(form, height=4)
        self.authors_list.grid(row=3, column=1, sticky=EW, pady=(5, 0))
        ttk.Button(form, text="Remove", command=self._remove_author).grid(row=3, column=2, sticky=EW+N, padx=(10, 0), pady=(5, 0))

        ttk.Label(form, text="License").grid(row=4, column=0, sticky=W, padx=(0, 10), pady=(10, 0))
        self.license = StringVar()
        # Identifiers listed in the BIDS "Licenses" appendix (1.11.1); any other value can be typed
        self.license_combobox = ttk.Combobox(form, textvariable=self.license, values=("PD", "PDDL", "CC0"))
        self.license_combobox.grid(row=4, column=1, columnspan=2, sticky=EW, pady=(10, 0))

    def _build_footer(self) -> None:
        footer = ttk.Frame(self, padding=20)
        footer.pack(side=BOTTOM, fill=X)

        ttk.Button(footer, text="Next", command=self._next).pack(side=RIGHT, padx=(10, 0))

        ttk.Style(self).configure("Error.TLabel", foreground="red")
        self.error = ttk.Label(footer, style="Error.TLabel")
        self.error.pack(side=LEFT, fill=X, expand=True)
        self.error.bind("<Configure>", lambda event: self.error.configure(wraplength=event.width))

    def _browse_folder(self) -> None:
        folder = filedialog.askdirectory(parent=self, title="Choose an empty folder for the dataset")
        if folder:
            self.folder.set(folder)

    def _add_author(self) -> None:
        author = self.author.get().strip()
        if author:
            self.authors_list.insert(END, author)
            self.author.set("")

    def _remove_author(self) -> None:
        for index in self.authors_list.curselection():
            self.authors_list.delete(index)

    def _next(self) -> None:
        name = self.name.get().strip()
        folder = self.folder.get().strip()
        missing = [label for label, value in (("Dataset name", name), ("Dataset folder", folder)) if not value]
        if missing:
            self.error.configure(text=f"Required: {', '.join(missing)}")
            return
        self.error.configure(text="")
