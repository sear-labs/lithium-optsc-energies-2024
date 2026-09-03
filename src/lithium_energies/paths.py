"""Where the data lives. Importable without building or solving the model.

Kept separate from model.py deliberately: importing model.py executes the whole
notebook top to bottom, including the solve. Anything that only needs to know
where files are - tests, scripts, tooling - imports this instead and pays
nothing.
"""
import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]

# Derived, not explicit. Override to point at another instance.
DATA_DIR = Path(os.environ.get("LITHIUM_DATA_DIR", _ROOT / "data" / "raw"))

# Everything a run produces goes here, so data/raw stays immutable and a second
# run reproduces the first.
RESULTS_DIR = Path(os.environ.get("LITHIUM_RESULTS_DIR", _ROOT / "results"))

WARM_START = DATA_DIR / "warm_start.sol"
