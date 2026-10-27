"""Batch import: from a folder of recordings, in any layout, to a validated conversion plan.

- patterns: extract raw entity values from a file path with user-written patterns.
- scan: walk a folder and apply the patterns to every supported recording file.
- labels: suggest a valid BIDS label from a raw value.
- plan: the conversion plan (one source file and its BIDS entities per recording) and its checks.
- mapping: read and write a plan as a TSV/CSV table, editable in a spreadsheet.
"""
