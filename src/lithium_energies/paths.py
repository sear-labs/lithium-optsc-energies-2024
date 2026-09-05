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


def check_data_dir(path=None):
    """Fail with the real reason when the data directory is not where we think.

    DATA_DIR is derived from this file's location, which is only correct inside
    a source checkout. After a plain `pip install` the package sits in
    site-packages and the derivation lands somewhere meaningless - and the data
    was never in the wheel to begin with, since it lives at the repo root. The
    naive symptom is "some_table.csv missing", which sends people looking for a
    corrupt download. Say what actually happened instead.
    """
    path = DATA_DIR if path is None else path
    if path.exists():
        return path
    raise FileNotFoundError(
        str(path) + " does not exist.\n\n"
        "The data ships with the REPOSITORY, not with the installed package, so\n"
        "`pip install git+https://...` gets you the code without it. Clone instead:\n\n"
        "    git clone https://github.com/sear-labs/lithium-optsc-energies-2024.git\n"
        "    cd lithium-optsc-energies-2024 && pip install -e .\n\n"
        "Or point $LITHIUM_DATA_DIR at a directory holding the data files."
    )
