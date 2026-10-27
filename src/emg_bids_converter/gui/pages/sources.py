"""Wizard page 3: find the recording files, in any folder layout, by patterns or from a mapping table"""

from pathlib import Path
from tkinter import *
from tkinter import filedialog, ttk

from ...batch.mapping import read_mapping
from ...batch.plan import SourceFile
from ...batch.scan import scan
from .page import Page

_HINT = ("One pattern per line, relative to the source folder; the first matching pattern is used. "
         "{subject} {session} {task} {acquisition} {run} {recording} capture a value, "
         "* matches any text, ** any number of folders. Example: {subject}/**/{task}_{run}.otb4")


class SourcesPage(Page):
    title = "Recording files"

    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(5, weight=1)

        ttk.Label(self, text="Source folder").grid(row=0, column=0, sticky=W, padx=(0, 10))
        self.source = StringVar()
        ttk.Entry(self, textvariable=self.source).grid(row=0, column=1, sticky=EW)
        ttk.Button(self, text="Browse…", command=self._browse_source).grid(row=0, column=2, padx=(10, 0))

        ttk.Label(self, text="Patterns").grid(row=1, column=0, sticky=NW, padx=(0, 10), pady=(10, 0))
        self.patterns = Text(self, height=3, width=20, wrap=NONE)
        self.patterns.grid(row=1, column=1, columnspan=2, sticky=EW, pady=(10, 0))
        hint = ttk.Label(self, text=_HINT, font=("TkDefaultFont", 10))
        hint.grid(row=2, column=1, columnspan=2, sticky=EW, pady=(2, 0))
        hint.bind("<Configure>", lambda event: hint.configure(wraplength=event.width))

        buttons = ttk.Frame(self)
        buttons.grid(row=3, column=0, columnspan=3, sticky=E, pady=(10, 0))
        ttk.Button(buttons, text="Scan", command=self._scan).pack(side=LEFT)
        ttk.Button(buttons, text="Import mapping…", command=self._import_mapping).pack(side=LEFT, padx=(10, 0))
        ttk.Button(buttons, text="Clear", command=self._clear).pack(side=LEFT, padx=(10, 0))

        self.summary = ttk.Label(self, text="No recording yet")
        self.summary.grid(row=4, column=0, columnspan=3, sticky=W, pady=(10, 0))
        self.unmatched_list = Listbox(self, height=3)
        self.unmatched_list.grid(row=5, column=0, columnspan=3, sticky=NSEW, pady=(5, 0))

    def _browse_source(self) -> None:
        folder = filedialog.askdirectory(parent=self, title="Choose the folder holding the recordings", mustexist=True)
        if folder:
            self.source.set(folder)

    def _scan(self) -> None:
        folder = self.source.get().strip()
        patterns = [line.strip() for line in self.patterns.get("1.0", END).splitlines() if line.strip()]
        if not folder or not patterns:
            self.show_error("Required to scan: Source folder and at least one pattern")
            return
        try:
            files, unmatched = scan(Path(folder), patterns)
        except (OSError, ValueError) as error:
            self.show_error(str(error))
            return
        self._merge(files, unmatched)

    def _import_mapping(self) -> None:
        path = filedialog.askopenfilename(parent=self, title="Choose a mapping table",
                                          filetypes=[("Mapping tables", "*.tsv *.csv")])
        if not path:
            return
        try:
            files = read_mapping(Path(path))
        except (OSError, ValueError) as error:
            self.show_error(str(error))
            return
        self._merge(files, [])

    def _merge(self, files: list[SourceFile], unmatched: list[Path]) -> None:
        # A file found again replaces its previous values: scanning again with a corrected pattern fixes it
        by_source = {file.source: file for file in self.wizard.files}
        by_source.update({file.source: file for file in files})
        self.wizard.files[:] = by_source.values()
        self.wizard.unmatched[:] = [path for path in dict.fromkeys(self.wizard.unmatched + unmatched)
                                    if path not in by_source]
        self.show_error("")
        self._refresh()

    def _clear(self) -> None:
        self.wizard.files.clear()
        self.wizard.unmatched.clear()
        self.wizard.overrides.clear()
        self._refresh()

    def _refresh(self) -> None:
        text = f"{len(self.wizard.files)} recording(s) found"
        if self.wizard.unmatched:
            text += f"; {len(self.wizard.unmatched)} file(s) matched no pattern and will not be converted:"
        self.summary.configure(text=text)
        self.unmatched_list.delete(0, END)
        for path in self.wizard.unmatched:
            self.unmatched_list.insert(END, str(path))

    def check(self) -> str | None:
        if not self.wizard.files:
            return "Scan a folder or import a mapping table to find the recordings"
        return None
