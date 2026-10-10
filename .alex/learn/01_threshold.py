# ruff: noqa: T201, E501
# Personal learning script (not library code), so it's exempt from the repo's lint rules (e.g. T201 no-print).
"""Monday exercise: see the QEC threshold yourself with Deltakit.

Run:   .venv/bin/python .alex/learn/01_threshold.py
Takes ~10-20s. Before running, write your PREDICTIONS in 01_walkthrough.md.

Pipeline (same 4 stages as the README quick start):
  1. Encode   - pick a code (rotated planar / surface code) and build a memory circuit
  2. Noise    - a QPU model adds physical noise at rate p to every operation
  3. Simulate - Stim (via deltakit_stim) samples detector flips, many shots
  4. Decode   - PyMatching (MWPM) guesses corrections; we count logical failures
"""

import os

os.environ["TQDM_DISABLE"] = "1"  # hide progress bars

from deltakit.circuit.gates import PauliBasis
from deltakit.decode import PyMatchingDecoder
from deltakit.decode.analysis import run_decoding_on_circuit
from deltakit.explorer.analysis import calculate_lep_and_lep_stddev
from deltakit.explorer.codes import RotatedPlanarCode, css_code_memory_circuit
from deltakit.explorer.qpu import QPU, ToyNoise

# TODO(Alex): add values to bracket the threshold more tightly.
PHYSICAL_ERROR_RATES = [0.002, 0.005, 0.01]
DISTANCES = [3, 5, 7]
SHOTS, BATCH = 200_000, 20_000


def logical_error_probability(p: float, d: int) -> tuple[float, float, int]:
    # 1. Encode: a d x d rotated planar code, memory experiment for d rounds, in the Z basis.
    code = RotatedPlanarCode(width=d, height=d)
    circuit = css_code_memory_circuit(code, num_rounds=d, logical_basis=PauliBasis.Z)

    # 2. Noise: ToyNoise applies depolarising-style noise with strength p.
    qpu = QPU(circuit.qubits, noise_model=ToyNoise(p=p))
    noisy = qpu.compile_and_add_noise_to_circuit(circuit)

    # 3 + 4. Build an MWPM decoder from the circuit's detector error model, sample, decode.
    decoder, stim_circuit = PyMatchingDecoder.construct_decoder_and_stim_circuit(noisy)
    result = run_decoding_on_circuit(stim_circuit, SHOTS, decoder, BATCH, min_fails=200)

    lep, stddev = calculate_lep_and_lep_stddev(result["fails"], result["shots"])
    return lep, stddev, len(circuit.qubits)


if __name__ == "__main__":
    print(f"{'p':>7} {'d':>3} {'qubits':>7} {'LEP':>10} {'+/-':>9}  trend")
    for p in PHYSICAL_ERROR_RATES:
        prev = None
        for d in DISTANCES:
            lep, sd, nq = logical_error_probability(p, d)
            trend = "" if prev is None else ("better" if lep < prev else "WORSE")
            print(f"{p:7.3f} {d:3d} {nq:7d} {lep:10.2e} {sd:9.1e}  {trend}", flush=True)
            prev = lep
        print()
