"""
Countermodels in the fully neutrosophic cell that contain BOTH a genuine glut
(some phi with P(phi) and P(~phi)) and a genuine gap (some phi with neither),
so that the cell is not witnessed merely by models of the other cells.
Re-checked with the independent evaluator of countermodels.py.
Usage: python genuine_full_cell.py > results_genuine_full_cell.txt
"""
from z3 import Or, And, Not, sat, is_true
from finite_models import build
from countermodels import evaluate

def search(goal, sizes):
    for (nW, nD) in sizes:
        s, P, G, conj, info = build(nW, nD, ())
        M = info["M"]; full = M - 1
        s.add(Or([And(P[m][w], P[full ^ m][w]) for m in range(M) for w in range(nW)]))           # a glut
        s.add(Or([And(Not(P[m][w]), Not(P[full ^ m][w])) for m in range(M) for w in range(nW)]))  # a gap
        if goal != "SAT":
            s.add(Not(conj[goal]))
        if s.check() == sat:
            mdl = s.model()
            Pos = {(m, w) for m in range(M) for w in range(nW) if is_true(mdl.eval(P[m][w], model_completion=True))}
            r = evaluate(nW, nD, Pos)
            glut = [(m, w) for (m, w) in Pos if (full ^ m, w) in Pos]
            gap = [(m, w) for m in range(M) for w in range(nW) if (m, w) not in Pos and (full ^ m, w) not in Pos]
            key = {"C": "PossG"}.get(goal, goal)
            ok = all(r[a] for a in ["A2", "A3", "A4", "A5"])
            print(f"full cell, goal {goal}: |W|={nW} |D|={nD} axioms A2-A5 hold={ok}, "
                  f"A1a={r['A1a']}, A1b={r['A1b']}, goal refuted={('n/a' if goal=='SAT' else not r[key])}")
            print(f"    gluts (mask,world): {sorted(glut)}")
            print(f"    gaps  (mask,world): {sorted(gap)}")
            print(f"    positive: {sorted(Pos)}  G extension: {r['_G_extension']}")
            print("    truth values: " + ", ".join(f"{k}={v}" for k, v in r.items() if not k.startswith('_')))
            return
    print(f"full cell, goal {goal}: no model with a glut and a gap up to sizes {sizes}")

if __name__ == "__main__":
    for goal in ["SAT", "C", "T3", "NecG", "MC"]:
        g = "T4" if goal == "NecG" else goal
        search(g, [(1, 1), (1, 2), (2, 1), (2, 2), (3, 1)])
