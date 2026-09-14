"""No committed file carries an absolute path from the machine that wrote it.

This repository shipped one. `notebooks/00_walkthrough.ipynb` carried a resolved
OneDrive path in its committed output, into the `v1.0.0` tag and into Zenodo
record 10.5281/zenodo.22309106, which is immutable. The notebook was fixed
afterwards and never re-released, so the deposit keeps it.

It was found by a peer session auditing the six DOI'd repositories after the same
defect turned up in `sav-osemosys-trd-2019`, not by anything here. This guard is
that repository's, taken rather than rebuilt.

It carries one allowlist entry: README.md quotes the original hardcoded input
directory to record what was fixed. That entry must keep matching something - a
stale allowlist entry fails the run rather than quietly widening what is ignored.

This does not duplicate `test_reproduces_paper.py::test_no_absolute_paths_in_source`,
and the difference between them is why the leak shipped. That test opens exactly one
file, `src/lithium_energies/model.py`, and asserts a Windows path is not in it. Its
name reads as a statement about the source tree; it is a statement about one module.
The leak was in `notebooks/00_walkthrough.ipynb`, which it never opens, so it passed
throughout - and the release it passed on is the one Zenodo archived.

Keep both. The narrow one names the file most likely to reintroduce the problem;
this one covers every committed file, including the artifacts a reader downloads.
A check that sounds tree-wide and is not is worse than no check, because its passing
gets read as coverage it never had.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "scripts" / "check_no_machine_paths.py"


def test_the_guard_script_exists():
    assert GUARD.exists(), f"{GUARD.name} is missing - the sweep is the whole protection"


def test_no_committed_file_carries_a_machine_path():
    result = subprocess.run([sys.executable, str(GUARD)], cwd=ROOT,
                            capture_output=True, text=True)
    assert result.returncode == 0, (
        "a committed file carries an absolute home path:\n"
        f"{result.stdout}{result.stderr}\n"
        "Fix it where the string is produced, not by normalising the artifact - "
        "a normaliser hides it from every reader who is not diffing bytes."
    )
