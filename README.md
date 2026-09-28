# Necessary existence is the modal collapse — machine-checked files

Code, TPTP problems and outputs for the paper

> M. Y. Leyva-Vázquez, *Necessary Existence Is the Modal Collapse: Scott's Ontological Argument under Gappy, Glutty and Neutrosophic Positivity* (manuscript submitted, 2026).

The paper shows that in the shallow embedding of higher-order modal logic S5 into classical HOL:

- **Theorem (NE is the collapse).** From Scott's definitions of essence and necessary existence alone, NE(x) holds at a world iff every truth is necessary.
- **Theorem (collapse or trivial positivity).** Axioms A2 and A5 alone entail MC ∨ ∀φ P(φ).
- A gap/glut map of Scott's axiom A1 split into A1a (no glut) and A1b (no gap), with finite countermodels.

## Contents

| Folder | What it contains |
|---|---|
| `tptp/` | TPTP THF problems. `base.ax` holds the explicit embedding (worlds `w`, S5 as universal accessibility) and Scott's definitions as equivalences; `base_lambda.ax` holds the same definitions as λ-equations. `A1a.ax` … `A5.ax` are the axioms and `c_*.p` the goals. `L_*.ax` are lemmas proved in an earlier step and re-used as premises. `verify_all.sh` runs every step. |
| `python/` | `finite_models.py`: finite (standard-semantics) model finder with Z3. `countermodels.py`: extracts the countermodels of the paper and re-checks them with a second, Z3-free implementation. `genuine_full_cell.py`: search for models with both a glut and a gap. |
| `results/` | Outputs used in the paper. |

## Reproduce

Requirements: Java 17+, [Leo-III 1.7.18](https://github.com/leoprover/Leo-III/releases/tag/v1.7.18), Python 3 with `z3-solver` (5.1.0 was used).

```bash
mkdir tools && curl -L -o tools/leo3.jar \
  https://github.com/leoprover/Leo-III/releases/download/v1.7.18/leo3-v1.7.18.jar
cd tptp && bash verify_all.sh          # 19 steps, all "SZS status Theorem"
cd ../python && python countermodels.py && python genuine_full_cell.py
```

Each line of `results_verify_all.txt` gives the step, the premises, the goal and the SZS status. Timeouts are 60 s per step without external provers.

## Notes

- The definitions are stated as universally quantified equivalences. With λ-equations Leo-III 1.7.18 did not prove some elementary lemmas within 60 s. Step `EQV` proves that the equivalence form entails the λ-form.
- Leo-III's native TPTP modal format treats bound variables as rigid (a `$o` variable ranges over truth values), so the explicit embedding is used instead.
- Uniqueness of Scott-essences (Lemma 3.1(3) of the paper) is proved by hand; Leo-III timed out on it.

## License

MIT (code). Leo-III is distributed separately under its own license.
