"""
Explicit countermodels for the paper, found with Z3 (finite_models.py) and
re-checked by an independent pure-Python evaluator of the axioms and goals.

Standard (full) finite models: every function D x W -> bool is a property.
A full model is in particular a Henkin model, so these are genuine
countermodels for the HOL embedding.

Usage: python countermodels.py > results_countermodels.txt
"""
import itertools
from z3 import sat, Not, is_true
from finite_models import build


def props(nW, nD):
    return list(range(1 << (nW * nD)))


def evaluate(nW, nD, Pos):
    """Pos: set of (mask, world) pairs that are positive. Returns dict of truth values."""
    bit = lambda x, w: x * nW + w
    has = lambda m, x, w: (m >> bit(x, w)) & 1 == 1
    M = 1 << (nW * nD); full = M - 1
    P = lambda m, w: (m, w) in Pos
    sub = lambda a, b: (a & ~b & full) == 0
    Wr, Dr = range(nW), range(nD)
    G = lambda x, w: all(has(m, x, w) for m in range(M) if P(m, w))
    Gmask = sum(1 << bit(x, w) for x in Dr for w in Wr if G(x, w))
    ess = lambda m, x, w: has(m, x, w) and all(sub(m, k) for k in range(M) if has(k, x, w))
    NE = lambda x, w: all(all(any(has(m, y, v) for y in Dr) for v in Wr) for m in range(M) if ess(m, x, w))
    NEmask = sum(1 << bit(x, w) for x in Dr for w in Wr if NE(x, w))
    neg = lambda m: full ^ m
    r = {}
    r["A1a"] = all(not (P(m, w) and P(neg(m), w)) for m in range(M) for w in Wr)
    r["A1b"] = all(P(m, w) or P(neg(m), w) for m in range(M) for w in Wr)
    r["A2"] = all(not P(a, w) or P(b, w) for a in range(M) for b in range(M) if sub(a, b) for w in Wr)
    r["A3"] = all(P(Gmask, w) for w in Wr)
    r["A4"] = all(not P(m, w) or P(m, v) for m in range(M) for w in Wr for v in Wr)
    r["A5"] = all(P(NEmask, w) for w in Wr)
    r["T1"] = all(not P(m, w) or m != 0 for m in range(M) for w in Wr)
    r["PossG"] = Gmask != 0
    r["T3"] = all(not G(x, w) or ess(Gmask, x, w) for x in Dr for w in Wr)
    r["NecG"] = all(any(G(x, w) for x in Dr) for w in Wr)
    r["MC"] = nW == 1          # full semantics: some proposition is contingent iff nW >= 2
    r["_G_extension"] = [(x, w) for x in Dr for w in Wr if G(x, w)]
    r["_positive"] = sorted(Pos)
    return r


def find(nW, nD, variant, goal):
    s, P, G, conj, info = build(nW, nD, variant)
    if goal != "SAT":
        s.add(Not(conj[goal]))
    if s.check() != sat:
        return None
    mdl = s.model()
    Pos = {(m, w) for m in range(info["M"]) for w in range(nW)
           if is_true(mdl.eval(P[m][w], model_completion=True))}
    return Pos


CASES = [
    ("paraconsistent (A1b only)", ("A1b",), "C", [(1, 1), (1, 2), (2, 1)]),
    ("paraconsistent (A1b only)", ("A1b",), "MC", [(2, 1), (2, 2)]),
    ("paracomplete (A1a only)", ("A1a",), "T3", [(1, 1), (1, 2), (2, 1), (2, 2)]),
    ("paracomplete (A1a only)", ("A1a",), "SAT", [(1, 1)]),
    ("full neutrosophic (neither)", (), "C", [(1, 1), (1, 2)]),
    ("full neutrosophic (neither)", (), "T3", [(1, 1), (1, 2), (2, 1), (2, 2)]),
    ("full neutrosophic (neither)", (), "MC", [(2, 1), (2, 2)]),
    ("classical (A1a+A1b)", ("A1a", "A1b"), "SAT", [(1, 1)]),
]

if __name__ == "__main__":
    for name, variant, goal, sizes in CASES:
        for (nW, nD) in sizes:
            Pos = find(nW, nD, variant, goal)
            if Pos is None:
                continue
            r = evaluate(nW, nD, Pos)
            axioms_ok = all(r[a] for a in ["A2", "A3", "A4", "A5"] + list(variant))
            goal_key = {"C": "PossG", "SAT": None}.get(goal, goal)
            refuted = "n/a" if goal_key is None else (not r[goal_key])
            tag = "MODEL" if goal == "SAT" else f"COUNTERMODEL to {goal}"
            print(f"{name:30s} {tag:22s} |W|={nW} |D|={nD}  re-check by a second, Z3-free implementation: axioms hold={axioms_ok}, "
                  f"goal refuted={refuted}")
            print(f"    truth values: " + ", ".join(f"{k}={v}" for k, v in r.items() if not k.startswith('_')))
            if not variant:
                print("    note: the fully neutrosophic cell ASSUMES neither A1a nor A1b; this model need not violate them "
                      "(a model of a cell with more axioms is a model of a cell with fewer). See genuine_full_cell.py.")
            print(f"    positive (mask,world): {r['_positive']}")
            print(f"    G extension (x,w): {r['_G_extension']}")
            break
        else:
            print(f"{name:30s} {goal}: none found at sizes {sizes}")
