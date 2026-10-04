"""Window to create an empty BIDS dataset"""

from tkinter import *
from tkinter import filedialog, ttk


class NewDatasetWindow(Toplevel):
    def __init__(self, parent: Tk) -> None:
        super().__init__(parent)
        self.title("New dataset")
        self._match_parent(parent)
        self.resizable(False, False)
        self._build_form()

    def _match_parent(self, parent: Tk) -> None:
        parent.update_idletasks()
        offset = int(parent.winfo_width() * 0.05)
        x = parent.winfo_x() + offset
        y = parent.winfo_y() + offset
        self.geometry(f"{parent.winfo_width()}x{parent.winfo_height()}+{x}+{y}")

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
