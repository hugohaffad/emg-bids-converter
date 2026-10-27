"""Suggest valid BIDS labels from the raw values found in file paths"""

import re


def suggest_label(entity: str, value: str) -> str:
    """Keep the digits of a run, the letters and digits of any other entity"""
    if entity == "run":
        return re.sub(r"[^0-9]", "", value)
    return re.sub(r"[^A-Za-z0-9]", "", value)


def natural_key(value: str) -> list:
    """Sort key putting "Patient 2" before "Patient 10\""""
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", value)]
