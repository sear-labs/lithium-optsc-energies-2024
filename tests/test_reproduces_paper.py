r"""Assert the published result, not an internal consistency property.

A teaching repo reconciles a hand-built notebook against its package. This repo
has no teaching notebook and no second implementation, so there is nothing to
reconcile against. What it must defend instead is the PAPER'S CLAIM: if a future
change silently alters the instance or moves the objective outside the band the
paper's own solve left open, that has to fail loudly.

Everything asserted here is quoted from Jones (2024), Energies 17, 2685:

  "The Cost Objective scenario's model had 13,556 rows, 10,706 continuous
   variables ... terminated ... and produced an objective value of 9.51e6, which
   corresponds to a total discounted cost of USD 9.51 trillion"
  "... total CO2 emissions of 56.8 gigatons"
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

PAPER_ROWS = 13556
PAPER_CONTINUOUS = 10706
PAPER_OBJECTIVE = 9.51e6          # USD millions -> USD 9.51 trillion
PAPER_CO2_GT = 56.8               # gigatons

# Why 0.5% and not something tighter: the model stops on a time limit with a
# residual MIP gap near 0.03%, so the published figure is an incumbent rather
# than a proven optimum. The three saved solutions from the original working
# folders span 9,511,432 to 9,511,782 - a spread of 0.004% - and a fresh
# warm-started 600 s run lands at 9,511,429. 0.5% comfortably contains that
# band while still catching any change that actually moves the answer.
OBJECTIVE_TOL = 5e-3


@pytest.fixture(scope="module")
def built():
    """Build the instance once and hand back the Gurobi model, unsolved."""
    import gurobipy as gp

    captured = {}
    real_optimize = gp.Model.optimize

    def stop_before_solving(self, *a, **k):
        self.update()
        captured["m"] = self
        return None

    gp.Model.optimize = stop_before_solving
    try:
        import lithium_energies.model  # noqa: F401  executes the model code
    except Exception:
        # Post-solve cells legitimately fail when we skip the solve; the model
        # object was captured before that point.
        pass
    finally:
        gp.Model.optimize = real_optimize

    if "m" not in captured:
        pytest.fail("the model was never constructed")
    return captured["m"]


def test_instance_matches_the_paper(built):
    """The rebuilt instance is the one the paper describes."""
    continuous = built.NumVars - (built.NumIntVars + built.NumBinVars)
    assert built.NumConstrs == PAPER_ROWS, (
        "constraint count drifted: %d, paper says %d" % (built.NumConstrs, PAPER_ROWS))
    assert continuous == PAPER_CONTINUOUS, (
        "continuous variable count drifted: %d, paper says %d"
        % (continuous, PAPER_CONTINUOUS))


def test_warm_start_is_present_and_is_an_input():
    """The warm start ships with the data and is never written back to.

    Imports lithium_energies.paths, NOT .model: importing the model executes the
    whole notebook including the solve. (Learned the hard way - the fixture's
    import raises on a post-solve cell, so Python never caches the module, and a
    second `import ...model` here started a real one-hour solve.)
    """
    from lithium_energies.paths import DATA_DIR, RESULTS_DIR, WARM_START

    ws = WARM_START
    assert ws.exists(), "warm start missing from data/raw - the run cannot reproduce"
    assert RESULTS_DIR != DATA_DIR, "results must not be written into data/raw"
    with open(ws) as fh:
        fh.readline()
        obj = float(fh.readline().split("=")[1])
    assert abs(obj - PAPER_OBJECTIVE) / PAPER_OBJECTIVE < OBJECTIVE_TOL, (
        "the shipped warm start is not the paper's solution: %.6e" % obj)


def test_no_credentials_in_source():
    """The original notebook carried Gurobi WLS credentials as literals."""
    import re

    src = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "src", "lithium_energies", "model.py")
    text = open(src, encoding="utf-8").read()
    for pattern in (r"WLSACCESSID", r"WLSSECRET", r"LICENSEID",
                    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"):
        assert not re.search(pattern, text), "credential-shaped literal in model.py: " + pattern


def test_no_absolute_paths_in_source():
    """Paths must be derived so the repo runs on a machine that is not Erick's."""
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "src", "lithium_energies", "model.py")
    text = open(src, encoding="utf-8").read()
    assert "C:" + chr(92) not in text, "absolute Windows path in model.py"


@pytest.mark.slow
def test_objective_matches_the_paper():
    """Full solve. Slow - deselect with -m 'not slow'.

    Run with a real time budget; a cold or short run will not get near the
    published incumbent and this test will (correctly) fail.
    """
    import gurobipy as gp

    seconds = int(os.environ.get("LITHIUM_SOLVE_SECONDS", "600"))
    captured = {}
    real_optimize = gp.Model.optimize

    def solve(self, *a, **k):
        self.update()
        self.Params.TimeLimit = seconds
        captured["m"] = self
        return real_optimize(self, *a, **k)

    gp.Model.optimize = solve
    try:
        import lithium_energies.model  # noqa: F401
    except Exception:
        pass
    finally:
        gp.Model.optimize = real_optimize

    m = captured.get("m")
    assert m is not None and m.SolCount, "no incumbent found in %d s" % seconds
    rel = abs(m.ObjVal - PAPER_OBJECTIVE) / PAPER_OBJECTIVE
    assert rel < OBJECTIVE_TOL, (
        "objective %.6e is %.4f%% from the paper's %.2e (tolerance %.1f%%)"
        % (m.ObjVal, 100 * rel, PAPER_OBJECTIVE, 100 * OBJECTIVE_TOL))


def test_every_write_goes_to_results():
    """No relative writes. They land in the caller's working directory.

    This regressed once: the extractor redirected Gurobi's m.write() calls but
    not pandas' df.to_excel(), so running the tests dropped variables.xlsx and
    constraints.xlsx into the repo root - breaking the one-way flow the README
    promises. Static check, so it cannot come back.
    """
    import re

    src = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "src", "lithium_energies", "model.py")
    text = open(src, encoding="utf-8").read()
    writers = re.findall(r"(?:m\.write|\.to_excel|\.to_csv|\.to_pickle|\.to_parquet)"
                         r"\(\s*['\"][^'\"]+['\"]", text)
    assert not writers, (
        "these writers use a relative path instead of RESULTS_DIR: %r" % writers)


def test_every_import_is_a_declared_dependency():
    """The package must import with nothing but what pyproject declares.

    `from IPython.display import Image` survived the notebook extraction as an
    unused line. IPython is not a dependency, so a clean `pip install` produced a
    package that could not import its own model - and the failure surfaced three
    layers away, as "model was never optimized", because the caller caught the
    ImportError as an expected post-build failure.

    Scanning the source is the cheap guard. Actually importing the module would
    execute the whole model.
    """
    import ast
    import os

    declared = {"pandas", "gurobipy", "openpyxl", "pytest"}
    stdlib = set(getattr(__import__("sys"), "stdlib_module_names", ()))
    src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "src", "lithium_energies")

    undeclared = {}
    for fn in os.listdir(src):
        if not fn.endswith(".py"):
            continue
        tree = ast.parse(open(os.path.join(src, fn), encoding="utf-8").read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""] if node.level == 0 else []
            else:
                continue
            for n in names:
                top = n.split(".")[0]
                if top and top not in stdlib and top not in declared \
                        and top != "lithium_energies":
                    undeclared.setdefault(top, set()).add(fn)

    assert not undeclared, (
        "imported but not declared in pyproject.toml: "
        + ", ".join("%s (%s)" % (k, ", ".join(sorted(v)))
                    for k, v in sorted(undeclared.items())))
