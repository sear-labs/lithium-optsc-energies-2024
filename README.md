# Lithium supply-chain optimisation — Energies 2024 paper model

[![Paper DOI](https://img.shields.io/badge/paper-10.3390%2Fen17112685-blue)](https://doi.org/10.3390/en17112685)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sear-labs/lithium-energies-2024/blob/main/notebooks/00_walkthrough.ipynb)

The optimisation model behind:

> Jones, E.C., Jr. **Lithium Supply Chain Optimization: A Global Analysis of Critical Minerals for
> Batteries.** *Energies* **2024**, 17, 2685. <https://doi.org/10.3390/en17112685>

A multi-period mixed-integer program over a five-stage lithium supply chain — mining, processing,
cathode, cell, pack — with a recycling loop, solved to 2100 under two objectives: minimum
discounted cost and minimum CO₂.

**This repository is frozen.** It exists so the published result can be checked, not to be developed
further. Ongoing modelling work lives elsewhere; corrections here become a new tagged version with a
new DOI rather than an edited history.

---

## Run it

```bash
pip install -e ".[dev]"
python scripts/run_all.py            # build the instance, check it against the paper (~5 s)
python scripts/run_all.py --solve 600 # also solve, warm-started, and report the gap
pytest -q                            # assert the paper's numbers
```

Gurobi is required — see *Licensing* below.

## What reproduces, and what does not

`scripts/run_all.py` rebuilds the model from `data/raw/` and checks it against what the paper
states. Both structural figures agree exactly:

| | rebuilt | paper |
|---|---:|---:|
| constraint rows | 13,556 | 13,556 |
| continuous variables | 10,706 | 10,706 |
| integer/binary variables | 2,673 | — |

Solving reproduces the published headline numbers to the precision the paper reports:

| | this repo (600 s) | paper |
|---|---:|---:|
| cost objective | 9,511,429 | 9.51 × 10⁶ → **USD 9.51 trillion** |
| CO₂ total | 56.75 Gt | **56.8 Gt** |

**The exact objective is not reproducible, by construction.** The model terminates on a time limit
with a residual MIP gap of roughly 0.03%, so the reported figure is an incumbent rather than a
proven optimum. The paper's own run was terminated at 100,800 s (28 h); a 600 s warm-started run
here lands 3 units away, which is well inside the gap either run leaves open. Different hardware,
thread counts or Gurobi versions will land somewhere else inside that band.

Three saved solutions in the original working folders illustrate the point: 9,511,432.14 (the
paper), 9,511,655.43, and 9,511,781.80. All three round to 9.51 × 10⁶.

`tests/test_reproduces_paper.py` asserts the structural figures exactly and the objective within a
documented tolerance.

## Verify it without a solver, without a licence

**Re-solving is the wrong verb.** This is a MIP that Gurobi could not close in 28 hours, finishing
with a ~0.03% gap open. Pointing an open-source solver at it and asking for the published number
sets you up to fail: CBC and HiGHS are good, but they will not beat Gurobi's overnight incumbent,
and if they found one it would be a *different* incumbent - that is what an open gap means.

**Checking is the right verb, and it is stronger.** `artifacts/` ships the frozen instance
(`model.mps`, `model.lp`) and the paper's solution (`solution.sol`). Given those, anyone can confirm
in seconds, with no solver installed and no licence, that the solution is feasible and that its
objective is the published figure:

```bash
python scripts/verify_solution.py            # needs only numpy
python scripts/verify_solution.py --relax    # + LP bound via HiGHS, which ships inside scipy
```

```
  13556 constraint rows, 13379 columns (2673 integer/binary)
  recomputed objective   9.5114321437e+06
  claimed in .sol        9.5114321437e+06   (delta 0.000e+00)
  worst row violation    7.451e-09
  worst bound violation  0.000e+00
  worst integrality err  0.000e+00
  FEASIBLE, and the objective is the published value

  LP bound               9.4916396678e+06
  integrality gap        0.2081%
```

That verification is exact, needs no licence, and reproduces bit for bit forever - none of which is
true of re-solving.

The `--relax` figure is the one thing an open-source solver contributes cheaply and usefully: the LP
relaxation sits **0.21% below** the incumbent, and closing that to 0.02% is what cost Gurobi 28
hours. It quantifies the problem's difficulty rather than pretending to reproduce it.

`scripts/verify_solution.py` includes a small hand-written MPS reader - PuLP's rejects the `LI`
bound type Gurobi writes, and `highspy` was not worth adding as a dependency for one file.

## Layout

```
artifacts/                       the frozen instance + the paper's solution. Committed on purpose.
data/raw/                        46 instance tables + the warm-start solution. Read-only.
src/lithium_energies/model.py    the model
scripts/run_all.py               build, check, optionally solve
notebooks/00_walkthrough.ipynb   thin notebook: imports the package, holds no logic
results/                         everything a run produces
tests/                           asserts the published numbers
```

`data/raw/` is immutable. **`warm_start.sol` is an input**, not an output — the model reads
it before optimising (see below). Anything a run produces is written to `results/`, so a run never
overwrites what it started from.

## The warm start

The model does not solve from cold. It reads `data/raw/warm_start.sol` as a MIP start
immediately before `optimize()`. This is faithful to the original notebook and is almost certainly
how the paper reached 28 hours of solve time — cumulatively, across successive warm-started runs.

Reproduction therefore requires shipping that file, which is why it lives in `data/raw/` and is
treated as instance data. Delete it and the run still works, but it starts cold and will not get
near the published objective in any reasonable time.

## Changes from the original notebook

The model is unchanged. Three things around it were fixed to make it runnable anywhere:

1. **Paths derived, not hardcoded.** All 43 loads pointed at
   `C:\Users\Jones\Downloads\jupyter_folder\input_csvs\`, a directory that exists on no current
   machine. They now resolve against `data/raw/`, overridable with `LITHIUM_DATA_DIR`.
2. **Case-insensitive input loading.** The code asks for `Cath_fixed_CO2.csv`; the file is
   `cath_fixed_CO2.csv`. Windows hides the mismatch; Linux, Colab and CI do not. Handled in the
   loader rather than by renaming the paper's data files.
3. **Credentials removed.** The notebook carried Gurobi WLS credentials as literals. The licence now
   comes from the environment.

## Licensing (Gurobi)

The model is far larger than the free `pip` licence allows. Locally, any full Gurobi licence works.

In Colab a node-locked licence cannot work — the VM differs every session — so use WLS credentials
stored as Colab secrets, never in the notebook:

```python
from google.colab import userdata
options = {
    "WLSACCESSID": userdata.get("GRB_WLSACCESSID"),
    "WLSSECRET":   userdata.get("GRB_WLSSECRET"),
    "LICENSEID":   int(userdata.get("GRB_LICENSEID")),   # userdata returns str; cast it
}
```

`SecretNotFoundError` on first run is expected for anyone who has not added those three secrets.

## Archiving

Tagged releases are archived to Zenodo, which issues a version DOI per release and a concept DOI
that always resolves to the latest. The code DOI badge goes here once the first release is archived;
it and the paper DOI should cross-reference each other.

Frozen means frozen: after a tagged release, a correction becomes a new version with a new DOI, not
an amended history. What the DOI resolves to must stay byte-identical to what was archived.

## How to cite

Cite **the paper** for the work and **this repository** for the code.

```bibtex
@article{jones2024lithium,
  author  = {Jones, Jr., Erick C.},
  title   = {Lithium Supply Chain Optimization: A Global Analysis of
             Critical Minerals for Batteries},
  journal = {Energies},
  volume  = {17},
  number  = {11},
  pages   = {2685},
  year    = {2024},
  doi     = {10.3390/en17112685}
}
```

**Code DOI:** not yet minted. Once this repository is connected to Zenodo and a release is tagged,
Zenodo issues two DOIs — a *version* DOI per release, and a **concept DOI that always resolves to
the latest version and never changes**. The concept DOI goes here and in `CITATION.cff`; it stays
correct for the life of the repository, so it is one edit rather than a per-release chore.

`CITATION.cff` in the repo root also gives GitHub's "Cite this repository" button.

## Citing

Cite the paper for the work and this repository for the code — `CITATION.cff` carries both.
