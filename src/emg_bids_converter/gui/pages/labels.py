"""Wizard page 4: turn each raw value found in the file paths into a BIDS label"""

from tkinter import *
from tkinter import ttk

from ...batch.labels import natural_key, suggest_label
from ...batch.patterns import ENTITIES
from ...core import check_entity
from .page import Page


class LabelsPage(Page):
    title = "BIDS labels"

    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rows: dict[str, tuple[str, str]] = {}  # tree item -> (entity, raw value)

        hint = ttk.Label(self, text="Each value found becomes a BIDS label: letters and digits only. "
                                    "Select one or more values to rename them.")
        hint.grid(row=0, column=0, sticky=EW)
        hint.bind("<Configure>", lambda event: hint.configure(wraplength=event.width))

        table = ttk.Frame(self)
        table.grid(row=1, column=0, sticky=NSEW, pady=(10, 0))
        self.tree = ttk.Treeview(table, columns=("entity", "value", "label"), show="headings", height=4)
        for column, width in (("entity", 90), ("value", 150), ("label", 100)):
            self.tree.heading(column, text=column.capitalize())
            self.tree.column(column, width=width, stretch=column != "entity")
        scrollbar = ttk.Scrollbar(table, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", lambda event: self._load_selected())

        editor = ttk.Frame(self)
        editor.grid(row=2, column=0, sticky=EW, pady=(10, 0))
        ttk.Label(editor, text="Label").pack(side=LEFT)
        self.label = StringVar()
        ttk.Entry(editor, textvariable=self.label, width=12).pack(side=LEFT, padx=(5, 10))
        ttk.Button(editor, text="Apply to selection", command=self._apply).pack(side=LEFT)
        ttk.Button(editor, text="Number selection", command=self._number).pack(side=RIGHT)

    def on_show(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.rows.clear()
        for entity in ENTITIES:
            values = {file.values[entity] for file in self.wizard.files if entity in file.values}
            labels = self.wizard.labels.setdefault(entity, {})
            for value in sorted(values, key=natural_key):
                label = labels.setdefault(value, suggest_label(entity, value))
                item = self.tree.insert("", END, values=(entity, value, label))
                self.rows[item] = (entity, value)

    def _load_selected(self) -> None:
        selection = self.tree.selection()
        if len(selection) == 1:
            self.label.set(self.tree.set(selection[0], "label"))

    def _apply(self) -> None:
        selection = self.tree.selection()
        label = self.label.get().strip()
        if not selection or not label:
            self.show_error("Select one or more values and type their label")
            return
        try:
            for entity in {self.rows[item][0] for item in selection}:
                check_entity(entity, label)
        except (TypeError, ValueError) as error:
            self.show_error(str(error))
            return
        for item in selection:
            self._set(item, label)
        self.show_error("")

    def _number(self) -> None:
        selection = self.tree.selection()
        entities = {self.rows[item][0] for item in selection}
        if len(entities) != 1:
            self.show_error("Select values of a single entity to number them")
            return
        items = sorted(selection, key=lambda item: natural_key(self.rows[item][1]))
        width = 1 if entities == {"run"} else max(2, len(str(len(items))))
        for number, item in enumerate(items, start=1):
            self._set(item, f"{number:0{width}d}")
        self.show_error("")

    def _set(self, item: str, label: str) -> None:
        entity, value = self.rows[item]
        self.wizard.labels[entity][value] = label
        self.tree.set(item, "label", label)

    def check(self) -> str | None:
        for entity, value in self.rows.values():
            try:
                check_entity(entity, self.wizard.labels[entity][value])
            except (TypeError, ValueError) as error:
                return f"{entity} {value!r}: {error}"
        return None
