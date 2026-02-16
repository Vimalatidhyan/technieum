# Legacy Archive

This directory contains files moved from the project root during the Round 2
repo cleanup. Nothing here is used by the running application.

## Contents

| Directory/file | Original location | Reason archived |
|---|---|---|
| `api_secondary/` | `api/routes/`, `api/models/`, `api/config.py` | Old secondary API stack superseded by `app/api/` |
| `reconx_enterprise/` | `reconx-enterprise/` | Duplicate enterprise folder — identical to `app/` after canonicalization |

## Rollback

To restore any file, simply `mv archive/legacy/<file> <original_path>`.
All archived files are intact.
