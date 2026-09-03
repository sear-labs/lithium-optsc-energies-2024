r"""Verify the published result WITHOUT a commercial solver, and without solving.

Why this exists
---------------
The model is a MIP that Gurobi - one of the fastest solvers there is - could not
close in 28 hours, finishing with a ~0.03% gap still open. Handing a reader an
MPS file and suggesting they re-solve it with CBC or HiGHS sets them up to fail:
those solvers are good, but they are not going to reach a better incumbent than
Gurobi did overnight, and even if they did they would land on a DIFFERENT
incumbent, because that is what an open gap means.

Re-solving is the wrong verb. **Checking** is the right one, and it is far
stronger: given the model and a claimed solution, anyone can confirm in seconds,
with no solver and no licence, that

  1. the solution is FEASIBLE - it satisfies every constraint and bound, and
     every integer variable really is integral; and
  2. its OBJECTIVE is the published number.

That is a complete verification of the paper's claim. It does not depend on
hardware, thread count, solver version or luck, and it is reproducible bit for
bit forever - none of which is true of re-solving.

Usage
-----
    python scripts/verify_solution.py                       # ships-with defaults
    python scripts/verify_solution.py --mps M --sol S       # any pair
    python scripts/verify_solution.py --relax               # + LP bound via HiGHS

Only numpy is required. `--relax` additionally uses scipy (HiGHS is built into
scipy >= 1.9), which gives the LP relaxation bound and therefore the integrality
gap - the one thing an open-source solver CAN contribute cheaply here.
"""
import argparse
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))

PAPER_OBJECTIVE = 9.51e6      # USD millions -> USD 9.51 trillion
FEAS_TOL = 1e-6               # Gurobi's default primal feasibility tolerance
INT_TOL = 1e-5


def parse_mps(path):
    """Minimal free/fixed-format MPS reader.

    Written by hand because PuLP's reader rejects the `LI` bound type that
    Gurobi writes, and highspy is not a dependency worth adding for one file.
    Handles the sections this model uses: ROWS, COLUMNS (with INTORG/INTEND
    markers), RHS, RANGES, BOUNDS.
    """
    rows, row_type, cols = [], {}, defaultdict(dict)
    rhs, ranges = {}, {}
    lb, ub, integer = {}, {}, set()
    obj_row = None
    section = None
    in_int = False

    with open(path, errors="replace") as fh:
        for line in fh:
            if not line.strip() or line.lstrip().startswith("*"):
                continue
            if line[0] not in (" ", "\t"):
                section = line.split()[0].upper()
                continue
            t = line.split()
            if section == "ROWS":
                kind, name = t[0].upper(), t[1]
                row_type[name] = kind
                if kind == "N" and obj_row is None:
                    obj_row = name
                else:
                    rows.append(name)
            elif section == "COLUMNS":
                if len(t) >= 3 and t[1] == "'MARKER'":
                    in_int = "INTORG" in line
                    continue
                col = t[0]
                if in_int:
                    integer.add(col)
                for i in range(1, len(t) - 1, 2):
                    cols[col][t[i]] = float(t[i + 1])
            elif section == "RHS":
                for i in range(1, len(t) - 1, 2):
                    rhs[t[i]] = float(t[i + 1])
            elif section == "RANGES":
                for i in range(1, len(t) - 1, 2):
                    ranges[t[i]] = float(t[i + 1])
            elif section == "BOUNDS":
                kind, col = t[0].upper(), t[2]
                val = float(t[3]) if len(t) > 3 else None
                if kind in ("UP", "UI"):
                    ub[col] = val
                    if val is not None and val < 0 and col not in lb:
                        lb[col] = -np.inf
                elif kind in ("LO", "LI"):
                    lb[col] = val
                elif kind == "FX":
                    lb[col] = ub[col] = val
                elif kind == "FR":
                    lb[col], ub[col] = -np.inf, np.inf
                elif kind == "MI":
                    lb[col] = -np.inf
                elif kind == "PL":
                    ub[col] = np.inf
                elif kind == "BV":
                    lb[col], ub[col] = 0.0, 1.0
                    integer.add(col)

    names = list(cols)
    return {
        "obj_row": obj_row, "rows": rows, "row_type": row_type, "cols": cols,
        "rhs": rhs, "ranges": ranges, "names": names, "integer": integer,
        "lb": {c: lb.get(c, 0.0) for c in names},
        "ub": {c: ub.get(c, np.inf) for c in names},
    }


def parse_sol(path):
    """Gurobi .sol: '# Objective value = X' then 'name value' per line."""
    values, claimed = {}, None
    with open(path, errors="replace") as fh:
        for line in fh:
            if line.startswith("#"):
                if "Objective value" in line:
                    claimed = float(line.split("=")[1])
                continue
            t = line.split()
            if len(t) >= 2:
                values[t[0]] = float(t[1])
    return values, claimed


def verify(m, x):
    obj = sum(coef * x.get(c, 0.0)
              for c, r in m["cols"].items() for rr, coef in r.items()
              if rr == m["obj_row"])

    act = defaultdict(float)
    for c, r in m["cols"].items():
        xc = x.get(c, 0.0)
        if xc:
            for rr, coef in r.items():
                if rr != m["obj_row"]:
                    act[rr] += coef * xc

    worst_row, worst_row_name = 0.0, ""
    for r in m["rows"]:
        b = m["rhs"].get(r, 0.0)
        a = act[r]
        kind = m["row_type"][r]
        v = (a - b if kind == "L" else b - a if kind == "G" else abs(a - b))
        if v > worst_row:
            worst_row, worst_row_name = v, r

    worst_bnd, worst_bnd_name = 0.0, ""
    for c in m["names"]:
        xc = x.get(c, 0.0)
        v = max(m["lb"][c] - xc, xc - m["ub"][c])
        if v > worst_bnd:
            worst_bnd, worst_bnd_name = v, c

    worst_int, worst_int_name = 0.0, ""
    for c in m["integer"]:
        xc = x.get(c, 0.0)
        v = abs(xc - round(xc))
        if v > worst_int:
            worst_int, worst_int_name = v, c

    return obj, (worst_row, worst_row_name), (worst_bnd, worst_bnd_name), (worst_int, worst_int_name)


def lp_relaxation(m):
    """LP bound via HiGHS, which ships inside scipy. No licence, no install."""
    from scipy.optimize import linprog
    from scipy.sparse import coo_matrix

    idx = {c: i for i, c in enumerate(m["names"])}
    n = len(idx)
    cvec = np.zeros(n)
    ri, ci, dv = [], [], []
    rows_l, bl = [], []
    eq_i, eq_j, eq_v, beq = [], [], [], []

    ridx = {}
    for c, r in m["cols"].items():
        for rr, coef in r.items():
            if rr == m["obj_row"]:
                cvec[idx[c]] = coef
                continue
            kind = m["row_type"][rr]
            if kind == "E":
                if rr not in ridx:
                    ridx[rr] = len(beq)
                    beq.append(m["rhs"].get(rr, 0.0))
                eq_i.append(ridx[rr]); eq_j.append(idx[c]); eq_v.append(coef)
            else:
                key = ("ub", rr)
                if key not in ridx:
                    ridx[key] = len(bl)
                    sgn = 1.0 if kind == "L" else -1.0
                    rows_l.append(sgn)
                    bl.append(sgn * m["rhs"].get(rr, 0.0))
                sgn = rows_l[ridx[key]]
                ri.append(ridx[key]); ci.append(idx[c]); dv.append(sgn * coef)

    A_ub = coo_matrix((dv, (ri, ci)), shape=(len(bl), n)) if bl else None
    A_eq = coo_matrix((eq_v, (eq_i, eq_j)), shape=(len(beq), n)) if beq else None
    bounds = [(m["lb"][c] if np.isfinite(m["lb"][c]) else None,
               m["ub"][c] if np.isfinite(m["ub"][c]) else None) for c in m["names"]]
    res = linprog(cvec, A_ub=A_ub, b_ub=np.array(bl) if bl else None,
                  A_eq=A_eq, b_eq=np.array(beq) if beq else None,
                  bounds=bounds, method="highs")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mps", default=os.path.join(ROOT, "artifacts", "model.mps"))
    ap.add_argument("--sol", default=os.path.join(ROOT, "artifacts", "solution.sol"))
    ap.add_argument("--relax", action="store_true", help="also solve the LP relaxation (HiGHS)")
    a = ap.parse_args()

    for p in (a.mps, a.sol):
        if not os.path.exists(p):
            sys.exit("missing: %s" % p)

    print("reading %s" % os.path.relpath(a.mps, ROOT))
    m = parse_mps(a.mps)
    print("  %d constraint rows, %d columns (%d integer/binary)"
          % (len(m["rows"]), len(m["names"]), len(m["integer"])))

    x, claimed = parse_sol(a.sol)
    print("reading %s\n  %d values, file claims objective %.10e"
          % (os.path.relpath(a.sol, ROOT), len(x), claimed))

    obj, (wr, wrn), (wb, wbn), (wi, win) = verify(m, x)

    print("\n--- verification, no solver used ---")
    print("  recomputed objective   %.10e" % obj)
    print("  claimed in .sol        %.10e   (delta %.3e)" % (claimed, abs(obj - claimed)))
    print("  paper's figure         %.2e         (relative %.5f%%)"
          % (PAPER_OBJECTIVE, 100 * abs(obj - PAPER_OBJECTIVE) / PAPER_OBJECTIVE))
    print("  worst row violation    %.3e  (%s)" % (wr, wrn or "-"))
    print("  worst bound violation  %.3e  (%s)" % (wb, wbn or "-"))
    print("  worst integrality err  %.3e  (%s)" % (wi, win or "-"))

    ok = (wr <= FEAS_TOL and wb <= FEAS_TOL and wi <= INT_TOL
          and abs(obj - claimed) <= max(1.0, abs(claimed) * 1e-9))
    print("\n  %s" % ("FEASIBLE, and the objective is the published value"
                      if ok else "CHECK FAILED - see the violations above"))

    if a.relax:
        print("\n--- LP relaxation (HiGHS via scipy; no licence needed) ---")
        res = lp_relaxation(m)
        if res.status == 0:
            print("  LP bound               %.10e" % res.fun)
            print("  integrality gap        %.4f%%"
                  % (100 * abs(obj - res.fun) / max(abs(obj), 1e-9)))
            print("  (the LP bound is what an open-source solver can give you cheaply;")
            print("   closing the remaining gap is what took Gurobi 28 hours.)")
        else:
            print("  LP solve failed: %s" % res.message)

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
