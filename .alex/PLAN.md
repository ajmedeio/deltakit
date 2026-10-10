# Deltakit contribution plan (Alex)

> **Branch-local notes. Do NOT include `.alex/` in any upstream PR.**
> This lives on the `alex/plan` branch only. Feature work happens on separate
> branches cut from `upstream/main` (see "Branch hygiene" below).

## Why

Build a real, public open-source track record in Riverlane's QEC SDK before
(and during) the application for **Director of Open-Source Software** at
Riverlane (College Park, MD). Quality over quantity: one thoughtful,
well-communicated contribution beats ten typo PRs.

## Targets

| Priority | Issue | What "done" looks like |
|---|---|---|
| 1 | [Deltakit/deltakit#51](https://github.com/Deltakit/deltakit/issues/51) — improve module import times | Investigation comment with data + diagram, then a PR adopting [SPEC-0001](https://scientific-python.org/specs/spec-0001/) / `lazy-loader` for at least one subpackage, with before/after numbers. |
| 2 | [Deltakit/deltakit-stim#21](https://github.com/Deltakit/deltakit-stim/issues/21) — propagate `deltakit_stim` name in `__str__`/`__repr__` | C++/pybind11 PR with updated binding tests. |
| Stretch | [Deltakit/deltakit#56](https://github.com/Deltakit/deltakit/issues/56) — test/document `use_iswap_gates` | Unit tests + docs explaining iSWAP-native generation vs CX→iSWAP compile. |
| Later | [Deltakit Community Fund](https://github.com/Deltakit/deltakit/issues/343) | Applications open **November 2026**. Revisit after the first PR lands. |

## Ground rules (from `docs/CONTRIBUTING.md`)

- Conventional Commits for commit messages and PR titles (`perf:`, `fix:`, `test:`, `docs:`…). Issues use `bug:` / `request:`.
- **CLA**: a bot asks on the first PR. Sign it.
- **No rebasing / force-pushing during review.** Use regular pushes and merge commits.
- Batch commits; CI runs on every push.
- **AI disclosure**: if an LLM influenced the contribution, say how in the PR description. Alex writes and understands every line. The agent helps with investigation, review and explanations.
- Run `just check` (lint + security + test) before pushing.

## Environment

- Repo: `~/repos/github.com/Deltakit/deltakit`
- Remotes: `origin` = `ajmedeio/deltakit` (fork), `upstream` = `Deltakit/deltakit`
- Tooling: `uv` (`~/.local/bin/uv`), `just` (installed via `uv tool install rust-just`)
- Setup: `uv sync` · tests: `just test` · full local CI: `just check` · docs: `just docs`
- Pre-commit: `uv run pre-commit install`

### Branch hygiene

```sh
git fetch upstream
git switch -c perf/lazy-imports upstream/main   # feature work, no .alex/
git push -u origin perf/lazy-imports
```

The plan branch is `alex/plan`. Update it at the end of each evening:

```sh
git switch alex/plan && git add .alex && git commit -m "dev: session log <date>" && git push
```

---

## Schedule (evenings, ~1.5–2h each)

### Sat Oct 10 — Setup ✅ (done with agent)
- [x] Clone, fork (`ajmedeio/deltakit`), remotes, `uv sync`, `just` installed
- [x] Baseline test run (see session log)
- [x] Baseline import-time measurement (see session log)

### Mon Oct 12 — Learn the codebase + QEC basics
- [ ] Skim `README.md`, `docs/` getting-started guide, and the package layout under `src/deltakit/` (`core`, `circuit`, `decode`, `explorer`)
- [ ] Work through [deltakit-textbook](https://github.com/Deltakit/deltakit-textbook) chapters 1–2 (repetition code, surface code basics)
- [ ] Run one notebook / quick-start end-to-end locally (generate a circuit → simulate with Stim → decode)
- [ ] `uv run pre-commit install`
- [ ] Re-read issue #51 thread, note who the maintainers are (`nelimee`, `rolandriver`, `mdhaber`)

### Tue Oct 13 — Investigate #51 (no code changes yet)
- [ ] Profile with `python -X importtime -c "import deltakit"` and per subpackage
- [ ] Visualize with [`tuna`](https://github.com/nschloe/tuna) (`uvx tuna importtime.log`), screenshot it
- [ ] Confirm/extend the Sat baseline (top offenders already identified: `error_budget`, `galois`, `_binomial_fit`, `deltakit_decode`). Trace *why* each is pulled in (which `__init__.py` line)
- [ ] Clone `Deltakit/deltakit-explorer` next to this repo and read its `analysis/__init__.py` and `codes/__init__.py`
- [ ] Read SPEC-0001 + `lazy-loader` docs; check `__init__.py` structure across subpackages
- [ ] Decide scope: which subpackage gives the biggest win with the smallest diff
- [ ] Draft the issue comment (data table + diagram + proposed approach + question about scope post-rearchitecture #332)

### Wed Oct 14 — Post on #51, start the branch
- [ ] Post the investigation comment on #51; ask to be assigned
- [ ] `git switch -c perf/lazy-imports upstream/main`
- [ ] Prototype layer 1 (meta-package): lazy `deltakit.Client` + lazy subpackage re-exports (`lazy.attach` / `.pyi` stubs so typing + docs still work)
- [ ] Only start layer 2 (deltakit-explorer) once a maintainer confirms that's wanted
- [ ] Verify: `mypy`, `pydoclint`, Sphinx docs still resolve symbols, tests green
- [ ] Add a regression guard (e.g. a test asserting heavy modules aren't in `sys.modules` after `import deltakit.<pkg>`)

### Thu Oct 15 — Polish + open PR
- [ ] Respond to any maintainer feedback on #51 and adjust scope
- [ ] Before/after numbers in a table; CHANGELOG entry if the repo expects one
- [ ] `just check` passes locally
- [ ] Open PR titled `perf: lazily import ...` referencing #51; include AI-usage disclosure; sign CLA
- [ ] Update session log

### Fri Oct 16 — Review loop + second contribution
- [ ] Address review comments (regular pushes, no force-push)
- [ ] Clone `Deltakit/deltakit-stim` to `~/repos/github.com/Deltakit/deltakit-stim`, build it, reproduce #21
- [ ] Comment on deltakit-stim#21 with findings / proposed approach

### Weekend Oct 17–18 (optional)
- [ ] deltakit-stim#21 PR
- [ ] Update `resume-riverlane.md` / cover letter with links to the issue comment + PR(s)

---

## Session log

Newest first. Each evening: what got done, what's blocked, exact next step.

### 2026-10-10 (Sat) — setup with agent
- Cloned `Deltakit/deltakit` @ `6c45d63`, forked to `ajmedeio/deltakit`, remotes configured (`origin` = fork, `upstream` = Deltakit). `main` tracks `upstream/main`.
- Installed `just` 1.58.0 via `uv tool install rust-just`. `uv sync --group test` succeeded.
- Baseline test run: **58 passed, 1 skipped** (`tests/qmem/test_qmem.py:249` needs `--slow`) in 25s.
- Baseline import times (Python 3.13, M-series Mac):
  - First-ever `import deltakit`: **12.3s** (cold: `.pyc` compilation, one-time).
  - Warm `import deltakit`: **~0.87s**. Each of `deltakit.circuit/explorer/decode/core`: ~0.85s, because they all go through the same eager chain.
  - `-X importtime` top cumulative offenders (µs):

    | Module | Cumulative |
    |---|---|
    | `deltakit` | 871,186 |
    | `deltakit_explorer` | 852,145 |
    | `deltakit_explorer.analysis` | 774,963 |
    | `deltakit_explorer.analysis.error_budget` (→ `_gradient`) | 514,642 |
    | `deltakit_explorer.codes` → `_bivariate_bicycle_code` → **`galois`** | ~185,000 |
    | `deltakit_explorer.analysis._binomial_fit` | 170,724 |
    | `deltakit_decode` (via `_run_all_analysis_engine`) | 164,917 |

- **Key finding:** this repo is a thin meta-package. `src/deltakit/__init__.py` does `from deltakit_explorer import Client`, so `import deltakit` eagerly loads *all* of `deltakit_explorer` just to expose `Client`. The real weight lives in the separate component repo **[Deltakit/deltakit-explorer](https://github.com/Deltakit/deltakit-explorer)** (`analysis/__init__.py`, `codes/__init__.py` eager imports; `galois` is a heavy third-party import).
- So #51 has two layers:
  1. **Meta-package (this repo):** make `deltakit.Client` and the `deltakit.<sub>` re-export modules lazy (module `__getattr__` / `lazy-loader`). Small, low-risk PR.
  2. **Component (deltakit-explorer):** lazy-load `analysis`/`codes` submodules and defer `galois`. Bigger win, but it belongs in a different repo, so ask maintainers where they want it (post-#332 split).
- **Next step:** Mon Oct 12 checklist.
