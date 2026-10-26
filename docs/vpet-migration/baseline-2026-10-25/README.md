# Digimon Alpha migration baseline

Baseline captured on 2026-10-25 before moving the V-Pet application to Vue.

## Purpose

This directory freezes the last known working Python/vanilla-JS implementation. It is the comparison point for the Vue migration: a migrated protocol is not considered complete until it can replay the relevant captures and preserve the confirmed hardware behavior documented here.

The source project has no Git repository, so this baseline uses an immutable ZIP plus SHA-256 hashes instead of a source commit.

## Frozen artifact

- Artifact: `artifacts/digimon-alpha-v12-source.zip`
- Size: 3,369,042 bytes
- SHA-256: `53e8f45fd640a20e13e92e4591b9966c9ee0a318454de7a2b8fd64cfec34da18`
- Firmware extension: `digimon-alpha-family-battle-v12`
- Python: 3.14.8
- Arduino CLI: 1.5.1

The artifact contains the battle engine, FastAPI server, vanilla frontend, WebUSB bridge, tests, firmware source and compiled Nano image, catalogs, probability configuration, all 112 serial captures, sprites and both migration spreadsheets. Runtime logs, `__pycache__` and the temporary `.codex_tmp_vpet` directory were intentionally excluded.

The local copy of `reference_book_2_with_images_and_appmon.xlsx` was locked by another process while packaging. The snapshot therefore contains the readable source workbook from `Digimon_Game`, which is the same workbook used by the application at runtime and contains 1,473 records.

## Verification at freeze time

```text
python -m unittest discover -v
Ran 100 tests in 1.397s
OK
```

`pytest` was not installed, so the existing `unittest` suite was used without changing the environment.

## Documents

- `DEVICE_MATRIX.md`: what worked on physical hardware, what has caveats and what remains untested.
- `CAPTURE_SUMMARY.json`: machine-readable inventory of the 112 recorded serial sessions.
- `SHA256SUMS.txt`: hashes for the archive and the files that define behavior.
- `REGRESSION_CHECKLIST.md`: acceptance gates for the Vue implementation.

## Restore and compare

To verify the archive without extracting it:

```powershell
Get-FileHash -Algorithm SHA256 .\artifacts\digimon-alpha-v12-source.zip
```

Do not edit the contents of this baseline. Changes for the migration belong in `frontend/src/features/vpet` and `backend/app/vpet`; new hardware evidence should be added as a new dated baseline or fixture set.
