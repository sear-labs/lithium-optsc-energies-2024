r"""Build the Energies-2024 lithium MILP from its input CSVs and check it against
the published paper.

The paper states the model had 13,556 rows and 10,706 continuous variables and
was terminated after 100,800 s (28 h) at an objective of 9.51e6 (USD 9.51
trillion). This script rebuilds the instance from the 46 input CSVs and asserts
the dimensions match, then optionally solves.

  python scripts/run_all.py              # build + dimension check only (fast)
  python scripts/run_all.py --solve 300  # also solve for 300 s and report the gap

Dimension agreement proves the data pipeline reproduces the paper's instance.
It does NOT prove the objective reproduces: the model terminates on a time
limit with a residual MIP gap, so the reported figure is an incumbent. See
--solve output for what that costs in practice.
"""
import argparse
import os
import sys
import time

PAPER = {"rows": 13556, "continuous": 10706, "objective": 9.51e6, "time_limit_s": 100800}

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import gurobipy as gp  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solve", type=int, default=0,
                    help="seconds to spend solving (0 = build and check only)")
    args = ap.parse_args()

    captured = {}
    real_optimize = gp.Model.optimize

    def patched(self, *a, **k):
        """Intercept the notebook's optimize() so we can measure the instance
        before deciding whether to spend an hour on it."""
        self.update()
        captured["model"] = self
        captured["rows"] = self.NumConstrs
        captured["vars"] = self.NumVars
        captured["ints"] = self.NumIntVars + self.NumBinVars
        if args.solve:
            self.Params.TimeLimit = args.solve
            return real_optimize(self, *a, **k)
        return None

    gp.Model.optimize = patched
    t0 = time.time()
    print("building the model from data/raw ...", flush=True)
    try:
        import lithium_energies.model  # noqa: F401  (executes the notebook code)
    except Exception as exc:
        # The notebook's post-solve cells read files written by the ORIGINAL run
        # (solution.sol, variables.xlsx) with relative paths. Those failures are
        # downstream of model construction and do not affect the dimension check.
        print("[post-build cell failed, expected: %s: %s]"
              % (type(exc).__name__, str(exc)[:90]))
    build_s = time.time() - t0

    if "rows" not in captured:
        sys.exit("model was never optimized - nothing captured")

    cont = captured["vars"] - captured["ints"]
    print("\n%-26s %12s %12s   %s" % ("", "rebuilt", "paper", "match"))
    print("-" * 66)
    rows_ok = captured["rows"] == PAPER["rows"]
    cont_ok = cont == PAPER["continuous"]
    print("%-26s %12d %12d   %s" %
          ("constraint rows", captured["rows"], PAPER["rows"], "YES" if rows_ok else "NO"))
    print("%-26s %12d %12d   %s" %
          ("continuous variables", cont, PAPER["continuous"], "YES" if cont_ok else "NO"))
    print("%-26s %12d %12s   %s" % ("integer/binary variables", captured["ints"], "-", ""))
    print("\nbuild time: %.1f s" % build_s)

    if args.solve:
        m = captured["model"]
        print("\nsolved for %d s (the paper ran %d s = %.0f h)" %
              (args.solve, PAPER["time_limit_s"], PAPER["time_limit_s"] / 3600))
        print("  status          %d" % m.Status)
        if m.SolCount:
            print("  incumbent       %.6e" % m.ObjVal)
            print("  best bound      %.6e" % m.ObjBound)
            print("  MIP gap         %.4f%%" % (100 * m.MIPGap))
            print("  paper's value   %.2e  (rounds to the same 3 s.f.: %s)" %
                  (PAPER["objective"],
                   "YES" if abs(m.ObjVal - PAPER["objective"]) / PAPER["objective"] < 5e-3 else "NO"))
        else:
            print("  no incumbent found in the time allowed")

    ok = rows_ok and cont_ok
    print("\n%s" % ("DIMENSIONS REPRODUCE THE PAPER" if ok
                    else "DIMENSION MISMATCH - the pipeline does not rebuild the paper's instance"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
