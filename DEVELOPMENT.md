# Development & run instructions

This file explains how to run the example `project_template.py`, rebuild the devcontainer, and view the generated LilyPond (`.ly`) and PDF outputs.

## Run locally in Codespaces (recommended)

1. Open the repository in GitHub Codespaces or in VS Code and Reopen in Container.
2. The devcontainer's `postCreateCommand` will run `pip install -r requirements.txt`. If you changed `requirements.txt`, rebuild the container: Command Palette → `Dev Containers: Rebuild Container`.
3. Start the example script:

```bash
python3 project_template.py
```

This will parse the example snippets, create `relative_score.ly` and then call `lilypond` to produce `relative_score.pdf`.

## Viewing the .ly and .pdf files in Codespaces / VS Code

- In the Explorer, open `relative_score.ly` to inspect the generated LilyPond source.
- Click `relative_score.pdf` in the Explorer to preview the PDF inside VS Code.

If the PDF does not open in the editor, download it using the three-dot menu in the Explorer and open it with your local PDF viewer.

## Running a web server to preview PDF in browser (optional)

You can serve the workspace directory and view the PDF via forwarded port 8888:

```bash
# serve current folder on port 8888
python3 -m http.server 8888 --bind 0.0.0.0
```

Then forward port 8888 in the Ports view (make it Public) and click the forwarded URL. Open `relative_score.pdf` in the browser.

## Composer helper

Use `src/composer.py` as a template-based entrypoint to create LilyPond and PDF files programmatically.

Example:

```bash
python -m src.composer --melody "\\relative c' { e4 f g a <c e g>2. r4 }" --harmony "c,2 g,2 <c e g>1" --output my_score
```

This will create `my_score.ly` and `my_score.pdf` (via Abjad/LilyPond) and can be used as the basis for composing automation.

## Notes
- `lilypond` is installed in the devcontainer image via the Dockerfile. Rebuild the container to pick up the change.
- If you want me to add a small `Makefile` or a convenience script (`run.sh`) to automate run → build → open, tell me and I’ll add it.

## CI and Git LFS notes

- The Dockerfile now installs `git-lfs` so pushes from within Codespaces will work for repositories that use LFS. If you still push from a local machine, ensure `git-lfs` is installed there as well.
- A GitHub Actions workflow `devcontainer-ci.yml` was added to build the devcontainer image and run the demo (`project_template.py`) on pull requests. The generated `relative_score.pdf` is uploaded as a workflow artifact for inspection.

## Canonical project file

`projectfile.md` is now the canonical project file for objectives, status and TODOs.
See `projectfile.md` in the repository root for the full project definition and the
study-file contract. `DEVELOPMENT.md` continues to include run/debug instructions and
the devcontainer notes.

## DEVELOPMENT file standard (project contract setting)

This repository treats `DEVELOPMENT.md` as the authoritative development-run
document and a project-level contract for contributors. The document must follow
this minimal standard so automated checks, contributors, and the template code
can rely on a stable structure.

Required contents
- Header: a short one-line title and a `DEVELOPMENT version: vX.Y` line near the top
	so tooling and reviewers can detect whether the document format changed.
- Run & devcontainer instructions: concise step-by-step instructions for
	starting the example script(s) and rebuilding the devcontainer, if applicable.
- Canonical pointer: a clear statement pointing to `projectfile.md` as the
	canonical projectfile for goals/status/TODOs.
- Contract summary: a short, explicit statement of the study-file vs template
	contract (where parsing/engraving live) and where to put musical inputs.
- Changelog entry for edits: when this file is modified, include a short
	changelog entry at the end of the file with the date, author, and a one-line
	summary of the change.

Edit process (how to change the contract)
- Small edits that do not change the contract (typos, clarifications) may be
	made directly on a branch and merged via PR following normal review.
- Any change that expands, reduces, or otherwise modifies the study-file
	contract MUST also update `projectfile.md`. The PR must include a short
	rationale and an entry in this file's changelog section.

Automation and enforcement
- Repositories depending on a strict workflow should add a small GitHub Actions
	check that validates the presence of the required header and the canonical
	pointer. If you want, I can add a simple Action that checks `DEVELOPMENT.md`
	for the `DEVELOPMENT version:` line and rejects PRs that update the contract
	without a matching `projectfile.md` update.

Minimal example header (copy into `DEVELOPMENT.md`):

````
# Development & run instructions

DEVELOPMENT version: v1.0 — 2025-09-24

...existing content...
````

Location and intent
- Keep this file in the repository root. It is intended for maintainers and
	future contributors to understand how to run the example, what the project
	contract is, and how to change it safely.

By placing this standard inside `DEVELOPMENT.md` we make the contract explicit
and discoverable. Follow the edit process above when you need to change the
contract or its wording.