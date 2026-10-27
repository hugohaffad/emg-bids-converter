"""Wizard page 2: *_emg.json fields shared by all the recordings"""

from tkinter import *
from tkinter import ttk

from .page import Page


class AcquisitionPage(Page):
    title = "Acquisition"

    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="EMG reference *").grid(row=0, column=0, sticky=W, padx=(0, 10))
        self.emg_reference = StringVar()
        # Values named by the BIDS EMGReference definition (1.11.1); otherwise the reference electrode name
        self.emg_reference_combobox = ttk.Combobox(self, textvariable=self.emg_reference,
                                                   values=("Bipolar", "ChannelSpecific"))
        self.emg_reference_combobox.grid(row=0, column=1, sticky=EW)

        ttk.Label(self, text="Power line frequency (Hz) *").grid(row=1, column=0, sticky=W, padx=(0, 10), pady=(10, 0))
        self.powerline_frequency = StringVar(value="50")
        self.powerline_frequency_combobox = ttk.Combobox(self, textvariable=self.powerline_frequency,
                                                         values=("50", "60"))
        self.powerline_frequency_combobox.grid(row=1, column=1, sticky=EW, pady=(10, 0))

    def check(self) -> str | None:
        if not self.emg_reference.get().strip():
            return "Required: EMG reference"
        try:
            frequency = float(self.powerline_frequency.get())
        except ValueError:
            return "Power line frequency must be a number in Hz"
        if frequency <= 0:
            return "Power line frequency must be positive"
        return None
