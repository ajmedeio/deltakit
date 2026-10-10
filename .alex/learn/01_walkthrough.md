# Monday walkthrough: Deltakit codebase + QEC basics (~1.5–2h)

Work top to bottom. Write answers inline; that turns this file into your study notes.

## Part 1: The mental model (20 min)

Read the [README](../../README.md) "Feature highlights" + "Quick Start", then
[docs/guide/getting_started.md](../../docs/guide/getting_started.md).

A QEC **memory experiment** asks: *if I store one logical qubit for `r` rounds, how often does it get corrupted?*

| Stage | What happens | Deltakit package (component repo) |
|---|---|---|
| Encode | Choose a code (e.g. rotated surface code, distance `d`) and build the circuit: data qubits + ancilla qubits that measure stabilisers each round | `deltakit.explorer.codes` (deltakit-explorer), circuit types in `deltakit.circuit` (deltakit-circuit) |
| Noise | Compile to a QPU's native gates and inject physical errors at rate `p` | `deltakit.explorer.qpu` |
| Simulate | Stim samples **detector** outcomes (a detector = "did this stabiliser measurement change unexpectedly?") over many shots | `deltakit_stim` (Riverlane's Stim fork) |
| Decode | A decoder (here MWPM / PyMatching) looks at detector flips, infers the most likely errors, and predicts whether the logical **observable** flipped. Wrong prediction = logical failure | `deltakit.decode`, graphs in `deltakit.core` |
| Analyse | LEP = failures/shots, then per-round LEP, Λ (suppression factor), QuOps... | `deltakit.explorer.analysis` |

Key vocabulary (write a one-line definition of each in your own words):
- **Code distance `d`:**
- **Stabiliser / syndrome:**
- **Detector:**
- **Logical observable:**
- **Detector error model (DEM):**
- **Threshold:**
- **Λ (Lambda):** how much the logical error rate drops each time `d` goes up by 2. Google's Willow result was Λ ≈ 2.

## Part 2: See the threshold yourself (30 min)

**Predict first** (no peeking at the output):
1. At `p = 0.002`, as `d` goes 3 → 5 → 7, does the logical error probability go up or down? By roughly how much?
   - My prediction:
2. At `p = 0.01`, same question.
   - My prediction:
3. Why do larger codes need more qubits? Count for `d = 3`: `d²` data + `d² − 1` ancillas = ?
   - My answer:

Then run it:

```sh
.venv/bin/python .alex/learn/01_threshold.py
```

Reference run from Sat Oct 10 (200k shots, PyMatching, ToyNoise):

| p | d=3 | d=5 | d=7 | bigger code is... |
|---|---|---|---|---|
| 0.002 | 1.70e-3 | 6.35e-4 | 1.65e-4 | **better** (~10× from d=3→7) |
| 0.010 | 3.83e-2 | 5.21e-2 | 5.97e-2 | worse |
| 0.015 | 7.66e-2 | 1.32e-1 | 1.86e-1 | worse |

Exercises:
- [ ] Edit `PHYSICAL_ERROR_RATES` to bracket the threshold more tightly (try 0.004, 0.006, 0.008). Roughly where is ToyNoise's threshold for this decoder? → __________
- [ ] Estimate Λ at `p = 0.002` from the table: LEP(d=3)/LEP(d=5) and LEP(d=5)/LEP(d=7). → __________
- [ ] Think about it: the README quick start uses `p = 0.01`. Given this table, what would a new user see if they increased `d` there? (Possible docs discussion later. **Don't open an issue yet.** Note it and raise it with a maintainer once you have rapport.)

## Part 3: Map the code (30 min)

The `deltakit` repo is a **meta-package**: thin re-export shims over the component packages.

```sh
cat src/deltakit/__init__.py          # Client from explorer (the #51 culprit)
cat src/deltakit/circuit/__init__.py  # from deltakit_circuit import *
cat src/deltakit/decode/__init__.py   # + cloud decoders from explorer
ls .venv/lib/python3.14/site-packages | grep deltakit   # where the real code lives
```

- [ ] Open the real source of one function you just used, e.g.
      `.venv/bin/python -c "import deltakit_explorer.codes as m, inspect; print(inspect.getsourcefile(m.css_code_memory_circuit))"`
      and skim it. What does a "round" consist of in the generated circuit?
- [ ] Print the circuit for d=3, 1 round: `print(circuit.as_stim_circuit())` (or `str(...)`). Find the `DETECTOR` and `OBSERVABLE_INCLUDE` lines.
- [ ] Read `tests/unit/test_namespace_reexports.py`. Explain in one sentence what it guarantees (this matters for #51):
  -

## Part 4: Textbook (remaining time)

[deltakit-textbook](https://github.com/Deltakit/deltakit-textbook) chapters 1–2 (repetition code, then surface code).
Optional: clone it to `~/repos/github.com/Deltakit/deltakit-textbook` and run the notebooks with this repo's venv.

## Wrap-up (5 min)

- [ ] Tick Monday's boxes in `../PLAN.md` and add a session-log line
- [ ] Commit + push `alex/plan`
