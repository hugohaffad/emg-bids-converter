"""Wizard page 1: dataset_description.json fields and the folder of the new dataset"""

from tkinter import *
from tkinter import filedialog, ttk

from .page import Page


class DatasetPage(Page):
    title = "Dataset"

    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Dataset name *").grid(row=0, column=0, sticky=W, padx=(0, 10))
        self.name = StringVar()
        self.name_entry = ttk.Entry(self, textvariable=self.name)
        self.name_entry.grid(row=0, column=1, columnspan=2, sticky=EW)
        self.name_entry.focus_set()

        ttk.Label(self, text="Dataset folder *").grid(row=1, column=0, sticky=W, padx=(0, 10), pady=(10, 0))
        self.folder = StringVar()
        self.folder_entry = ttk.Entry(self, textvariable=self.folder)
        self.folder_entry.grid(row=1, column=1, sticky=EW, pady=(10, 0))
        ttk.Button(self, text="Browse…", command=self._browse_folder).grid(row=1, column=2, padx=(10, 0), pady=(10, 0))

        ttk.Label(self, text="Authors").grid(row=2, column=0, sticky=W, padx=(0, 10), pady=(10, 0))
        self.author = StringVar()
        self.author_entry = ttk.Entry(self, textvariable=self.author)
        self.author_entry.grid(row=2, column=1, sticky=EW, pady=(10, 0))
        self.author_entry.bind("<Return>", lambda event: self._add_author())
        ttk.Button(self, text="Add", command=self._add_author).grid(row=2, column=2, sticky=EW, padx=(10, 0), pady=(10, 0))

        self.authors_list = Listbox(self, height=4)
        self.authors_list.grid(row=3, column=1, sticky=EW, pady=(5, 0))
        ttk.Button(self, text="Remove", command=self._remove_author).grid(row=3, column=2, sticky=EW+N, padx=(10, 0), pady=(5, 0))

        ttk.Label(self, text="License").grid(row=4, column=0, sticky=W, padx=(0, 10), pady=(10, 0))
        self.license = StringVar()
        # Identifiers listed in the BIDS "Licenses" appendix (1.11.1); any other value can be typed
        self.license_combobox = ttk.Combobox(self, textvariable=self.license, values=("PD", "PDDL", "CC0"))
        self.license_combobox.grid(row=4, column=1, columnspan=2, sticky=EW, pady=(10, 0))

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

    def check(self) -> str | None:
        name = self.name.get().strip()
        folder = self.folder.get().strip()
        missing = [label for label, value in (("Dataset name", name), ("Dataset folder", folder)) if not value]
        if missing:
            return f"Required: {', '.join(missing)}"
        return None
