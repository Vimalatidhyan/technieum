# Archive: context files for AI agents

These concatenated files are used by the **onboard-reconx** Cursor/Claude skill. Do not delete; the skill reads from here.

- **ProductDocumentation.txt** — README + architecture + pipeline
- **SolutionFileStructure.txt** — Repo file tree
- **DomainModels.txt** — Pydantic + SQLAlchemy models
- **Services.txt** — API route implementations
- **Presentation.txt** — Web UI HTML

Regenerate from source if the codebase changes (see `tests/generate_context_files.py` or equivalent).
