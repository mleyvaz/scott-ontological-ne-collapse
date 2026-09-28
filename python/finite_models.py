"""
Finite (standard-semantics) model finder for Scott's variant of Goedel's
ontological argument with a neutrosophic positivity cut.

Positivity at cut alpha is a pair of predicates on properties:
  p(phi)  <=>  T_pos(phi) >= alpha        (phi is positive)
  n(phi)  <=>  F_pos(phi) >= alpha        (phi is negative)
Neutrosophic negation swaps T and F, so n(phi) <=> p(~phi).
Goedel's A1 splits into
  A1a  no glut : ~(p(phi) & p(~phi))
  A1b  no gap  :  p(phi) | p(~phi)
Classical = A1a+A1b, paracomplete = A1a, paraconsistent = A1b, full = none.

Model: nW worlds (S5 = universal accessibility), nD individuals (constant
domain). Properties = ALL functions D x W -> bool (full/standard semantics),
encoded as bitmasks. p is world-relative: P[m][w].

A countermodel found here is a genuine countermodel (standard models are
Henkin models). Absence of a countermodel up to a size is NOT a proof.

CAVEAT (found 28-sep-2026): in full semantics the haecceity property
{(x,w)} exists, so every essence of x at w is that singleton and NE is empty
whenever nW >= 2. Hence any model containing a God-like being has one world,
and "no countermodel to MC" here is an artefact of full semantics. Henkin
countermodels (restricted property domains, as Nitpick builds) are needed.
"""
import itertools
import json
import sys
from z3 import Bool, Solver, And, Or, Not, Implies, BoolVal, sat, unsat, is_true


def build(nW, nD, variant, extra=()):
    nb = nW * nD
    M = 1 << nb
    bit = lambda x, w: x * nW + w
    has = lambda m, x, w: (m >> bit(x, w)) & 1 == 1
    full = M - 1
    neg = lambda m: full ^ m
    sub = lambda a, b: (a & ~b) == 0          # a subseteq b (as necessarily-implies)

    P = [[Bool(f"P_{m}_{w}") for w in range(nW)] for m in range(M)]
    s = Solver()

    # A1 variants
    for m in range(M):
        for w in range(nW):
            if "A1a" in variant:
                s.add(Not(And(P[m][w], P[neg(m)][w])))
            if "A1b" in variant:
                s.add(Or(P[m][w], P[neg(m)][w]))
    # A2: P(phi) & [](phi => psi) -> P(psi)
    for a in range(M):
        for b in range(M):
            if a != b and sub(a, b):
                for w in range(nW):
                    s.add(Implies(P[a][w], P[b][w]))
    # A4: P(phi) -> []P(phi)
    for m in range(M):
        for w in range(nW):
            for v in range(nW):
                s.add(Implies(P[m][w], P[m][v]))

    # G(x,w) symbolic
    G = [[And([Implies(P[m][w], BoolVal(has(m, x, w))) for m in range(M)])
          for w in range(nW)] for x in range(nD)]

    def P_of_symbolic(prop, w):  # P applied to a symbolic property prop[x][w]
        cases = []
        for m in range(M):
            eq = And([prop[x][v] == BoolVal(has(m, x, v)) for x in range(nD) for v in range(nW)])
            cases.append(And(eq, P[m][w]))
        return Or(cases)

    # A3: P(G)
    for w in range(nW):
        s.add(P_of_symbolic(G, w))

    # ess for concrete masks, NE mask (concrete: independent of P)
    def ess_c(m, x, w):
        if not has(m, x, w):
            return False
        return all(sub(m, k) for k in range(M) if has(k, x, w))
    NEmask = 0
    for x in range(nD):
        for w in range(nW):
            # NE(x,w): every essence phi of x is necessarily exemplified: forall v exists y phi(y,v)
            ok = all(all(any(has(m, y, v) for y in range(nD)) for v in range(nW))
                     for m in range(M) if ess_c(m, x, w))
            if ok:
                NEmask |= 1 << bit(x, w)
    for w in range(nW):  # A5: P(NE)
        s.add(P[NEmask][w])

    def ess_G(x, w):
        return And(G[x][w], And([Implies(BoolVal(has(k, x, w)),
                                          And([Implies(G[y][v], BoolVal(has(k, y, v)))
                                               for y in range(nD) for v in range(nW)]))
                                  for k in range(M)]))

    conj = {
        "T1": And([Implies(P[m][w], BoolVal(m != 0)) for m in range(M) for w in range(nW)]),
        "C": Or([G[x][w] for x in range(nD) for w in range(nW)]),
        "T3": And([Implies(G[x][w], ess_G(x, w)) for x in range(nD) for w in range(nW)]),
        "T4": And([Or([G[x][w] for x in range(nD)]) for w in range(nW)]),
        # MC over full semantics: every proposition non-contingent <=> nW==1
        "MC": BoolVal(nW == 1),
    }
    return s, P, G, conj, dict(M=M, NEmask=NEmask)


def check(nW, nD, variant, goal):
    s, P, G, conj, info = build(nW, nD, variant)
    if goal == "SAT":
        r = s.check()
    else:
        s.add(Not(conj[goal]))
        r = s.check()
    out = {"nW": nW, "nD": nD, "variant": "+".join(variant) or "none", "goal": goal, "result": str(r)}
    if r == sat:
        mdl = s.model()
        pos = sorted({m for m in range(info["M"]) for w in range(nW) if is_true(mdl.eval(P[m][w], model_completion=True))})
        gm = [[is_true(mdl.eval(G[x][w], model_completion=True)) for w in range(nW)] for x in range(nD)]
        out["positive_masks"] = pos
        out["G_extension"] = gm
        out["NE_mask"] = info["NEmask"]
    return out


if __name__ == "__main__":
    variants = {"classical": ("A1a", "A1b"), "paracomplete": ("A1a",),
                "paraconsistent": ("A1b",), "full_neutrosophic": ()}
    sizes = [(1, 1), (1, 2), (2, 1), (2, 2), (3, 2), (2, 3)]
    goals = ["SAT", "T1", "C", "T3", "T4", "MC"]
    results = []
    for name, v in variants.items():
        for goal in goals:
            found = None
            for (nW, nD) in sizes:
                r = check(nW, nD, v, goal)
                if r["result"] == "sat":
                    found = r
                    break
            label = ("model found" if goal == "SAT" else "COUNTERMODEL") if found else "none up to size"
            print(f"{name:18s} {goal:4s} -> {label}" + (f"  (W={found['nW']}, D={found['nD']})" if found else ""))
            results.append({"variant": name, "goal": goal, "found": found})
            sys.stdout.flush()
    with open("results_finite_models.json", "w") as f:
        json.dump(results, f, indent=1)
