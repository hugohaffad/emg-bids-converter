"""Wizard page 5: the final BIDS entities of every recording, with fixes for the exceptions"""

from pathlib import Path
from tkinter import *
from tkinter import filedialog, ttk

from ...batch.mapping import write_mapping
from ...batch.patterns import ENTITIES
from ...batch.plan import SourceFile, build_plan, check_plan
from ...core import check_entity
from .page import Page


class ReviewPage(Page):
    title = "Review"

    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rows: dict[str, SourceFile] = {}  # tree item -> source file

        hint = ttk.Label(self, text="To fix exceptions: select recordings, choose an entity, "
                                    "type its label (empty to remove it) and apply.")
        hint.grid(row=0, column=0, sticky=EW)
        hint.bind("<Configure>", lambda event: hint.configure(wraplength=event.width))

        table = ttk.Frame(self)
        table.grid(row=1, column=0, sticky=NSEW, pady=(10, 0))
        self.tree = ttk.Treeview(table, columns=("file", *ENTITIES), show="headings", height=4)
        for column in ("file", *ENTITIES):
            self.tree.heading(column, text=column.capitalize())
            self.tree.column(column, width=60, stretch=False)
        self.tree.column("file", width=150, stretch=True)
        scrollbar = ttk.Scrollbar(table, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        editor = ttk.Frame(self)
        editor.grid(row=2, column=0, sticky=EW, pady=(10, 0))
        self.entity = StringVar(value="session")
        ttk.Combobox(editor, textvariable=self.entity, values=ENTITIES, state="readonly", width=11).pack(side=LEFT)
        self.value = StringVar()
        ttk.Entry(editor, textvariable=self.value, width=10).pack(side=LEFT, padx=(5, 10))
        ttk.Button(editor, text="Apply to selection", command=self._apply).pack(side=LEFT)
        ttk.Button(editor, text="Export mapping…", command=self._export).pack(side=RIGHT)

    def _final_values(self, file: SourceFile) -> dict[str, str]:
        values = {entity: self.wizard.labels.get(entity, {}).get(value, value) for entity, value in file.values.items()}
        values.update(self.wizard.overrides.get(file.source, {}))
        return {entity: value for entity, value in values.items() if value}

    def on_show(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.rows.clear()
        for file in self.wizard.files:
            values = self._final_values(file)
            name = f"{file.source.parent.name}/{file.source.name}"
            item = self.tree.insert("", END, values=(name, *(values.get(entity, "") for entity in ENTITIES)))
            self.rows[item] = file
        self._show_used_columns()

    def _show_used_columns(self) -> None:
        used = {entity for item in self.rows for entity in ENTITIES if self.tree.set(item, entity)}
        self.tree.configure(displaycolumns=("file", *(e for e in ENTITIES if e in used or e in ("subject", "task"))))

    def _apply(self) -> None:
        selection = self.tree.selection()
        entity = self.entity.get()
        value = self.value.get().strip()
        if not selection:
            self.show_error("Select one or more recordings first")
            return
        if value:
            try:
                check_entity(entity, value)
            except (TypeError, ValueError) as error:
                self.show_error(str(error))
                return
        for item in selection:
            self.wizard.overrides.setdefault(self.rows[item].source, {})[entity] = value or None
            self.tree.set(item, entity, value)
        self._show_used_columns()
        self.show_error("")

    def _export(self) -> None:
        error = self.check()
        if error:
            self.show_error(error)
            return
        path = filedialog.asksaveasfilename(parent=self, title="Save the mapping table", defaultextension=".tsv",
                                            filetypes=[("Tab-separated table", "*.tsv"), ("Comma-separated table", "*.csv")])
        if not path:
            return
        try:
            write_mapping(self.wizard.plan, Path(path))
        except OSError as error:
            self.show_error(str(error))

    def check(self) -> str | None:
        files = [SourceFile(file.source, self._final_values(file)) for file in self.wizard.files]
        try:
            plan = build_plan(files)
            check_plan(plan)
        except (OSError, TypeError, ValueError) as error:
            return str(error)
        self.wizard.plan = plan
        return None
