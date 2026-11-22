# MCLab website: current source and baseline

The live site is **https://mclab-dgist.github.io/**. As confirmed on **2026-11-22**,
the authoritative editable site is **`main:mclab/`**, not the retained al-folio
template at the repository root. For MCLab work, follow this section and
[`mclab/README_KO.md`](mclab/README_KO.md); the legacy guidance below applies only
to explicitly requested work on the unused template.

## Single-source rules

- Edit records in `mclab/content/` and templates/assets in `mclab/`.
- Never edit `gh-pages`, `_site/`, or generated `data/site-data.js` as source.
- Do not restore old ZIP packages, generated snapshots, migration reports, or
  prior commits over current content. Fetch the current `main` before editing.
- Preserve all current content, including older-year publications and completed
  projects, unless the user explicitly requests a particular deletion.
- `mclab/quality/approved-baseline.json` is a **validation-only** reviewed lockfile,
  not an alternative content source. It protects all stable fields, item order,
  and current CSS/JavaScript. Update only entries corresponding to the user's
  intended change, in the same commit as that source change. Never automatically
  replace the baseline to make a failed check pass.
- Preserve the initial-install marker `mclab/.mclab-import.json`; the original
  installation ZIP is no longer required. Do not alter deployment workflows,
  rewrite Git history, or force-push without explicit authorization for that scope.

## Required MCLab checks

From the repository root:

```sh
python3 -m unittest discover -s .github/mclab -p 'test_*.py' -v
cd mclab
python3 -m unittest discover -s tests -v
python3 scripts/build_site.py
python3 scripts/verify_approved_release.py
```

Preview only the newly generated `mclab/_site/`, or create a portable preview with
`python3 scripts/build_preview.py`. Do not open source HTML as a data snapshot.
Review the diff against the current baseline and stage only explicit paths.
After committing to `main`, wait for both the MCLab deployment workflow and the
GitHub Pages deployment, then verify the public page before reporting completion.
MCLab uses Python 3.11+ and standard-library tests; it does not use the root
Jekyll/Docker build. Do not reformat or rebuild the unrelated legacy template.

---

# Retained al-folio template guidelines (not the live MCLab site)

A simple, clean, and responsive Jekyll theme for academics.

## Quick Links by Role

- **Are you a coding agent?** → Read [`.github/copilot-instructions.md`](.github/copilot-instructions.md) first (tech stack, build, CI/CD, common pitfalls & solutions)
- **Customizing the site?** → See [`.github/agents/customize.agent.md`](.github/agents/customize.agent.md)
- **Writing documentation?** → See [`.github/agents/docs.agent.md`](.github/agents/docs.agent.md)
- **Need setup/deployment help?** → [INSTALL.md](INSTALL.md)
- **Troubleshooting & FAQ?** → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Customization & theming?** → [CUSTOMIZE.md](CUSTOMIZE.md)
- **Quick 5-min start?** → [QUICKSTART.md](QUICKSTART.md)

## Essential Commands

### Local Development (Docker)

The recommended approach is using Docker.

```bash
# Initial setup & start dev server
docker compose pull && docker compose up
# Site runs at http://localhost:8080

# Rebuild after changing dependencies or Dockerfile
docker compose up --build

# Stop containers and free port 8080
docker compose down
```

### Pre-Commit Checklist

Before every commit, you **must** run these steps:

1.  **Format Code:**
    ```bash
    # (First time only)
    npm install --save-dev prettier @shopify/prettier-plugin-liquid
    # Format all files
    npx prettier . --write
    ```
2.  **Build Locally & Verify:**

    ```bash
    # Rebuild the site
    docker compose up --build

    # Verify by visiting http://localhost:8080.
    # Check navigation, pages, images, and dark mode.
    ```

## Critical Configuration

When modifying `_config.yml`, these **must be updated together**:

- **Personal site:** `url: https://username.github.io` + `baseurl:` (empty)
- **Project site:** `url: https://username.github.io` + `baseurl: /repo-name/`
- **YAML errors:** Quote strings with special characters: `title: "My: Cool Site"`

## Development Workflow

- **Git & Commits:** For commit message format and Git practices, see [.github/GIT_WORKFLOW.md](.github/GIT_WORKFLOW.md).
- **Code-Specific Instructions:** Consult the relevant instruction file for your code type.

| File Type                                     | Instruction File                                                                                |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Markdown content (`_posts/`, `_pages/`, etc.) | [markdown-content.instructions.md](.github/instructions/markdown-content.instructions.md)       |
| YAML config (`_config.yml`, `_data/`)         | [yaml-configuration.instructions.md](.github/instructions/yaml-configuration.instructions.md)   |
| BibTeX (`_bibliography/`)                     | [bibtex-bibliography.instructions.md](.github/instructions/bibtex-bibliography.instructions.md) |
| Liquid templates (`_includes/`, `_layouts/`)  | [liquid-templates.instructions.md](.github/instructions/liquid-templates.instructions.md)       |
| JavaScript (`_scripts/`)                      | [javascript-scripts.instructions.md](.github/instructions/javascript-scripts.instructions.md)   |

## Common Issues

For troubleshooting, see:

- [Common Pitfalls & Workarounds](.github/copilot-instructions.md#common-pitfalls--workarounds) in copilot-instructions.md
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions
- [GitHub Issues](https://github.com/alshedivat/al-folio/issues) to search for your specific problem.
