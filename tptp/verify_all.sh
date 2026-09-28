#!/bin/bash
# Reproduces every machine-checked step of the paper with its exact premises.
# Leo-III 1.7.18, Java 17. Usage: bash verify_all.sh > results_verify_all.txt
LEO="../tools/leo3.jar"; mkdir -p work
step () { # id base timeout conj premises...
  id=$1; base=$2; to=$3; conj=$4; shift 4
  f=work/step_$id.p; cat $base "$@" $conj > $f
  r=$(timeout $((to+30)) java -jar $LEO $f -t $to 2>&1 | grep -o "SZS status [A-Za-z]*" | head -1)
  echo "$id | base=$base | premises: $* | goal: $conj | ${r:-NO_ANSWER}"
}
echo "# sanity checks"
step SAN1 base.ax 30 c_TRIV.p
echo "# A1 halves"
step T1   base.ax 60  c_T1.p   A1a.ax A2.ax
step T3   base_lambda.ax 120 c_T3.p A1b.ax A4.ax
echo "# paracomplete chain (no A1b, no A4)"
step C    base.ax 60  c_C.p    L_T1.ax A3.ax
step GNE  base.ax 60  c_GNE.p  A5.ax
step CNE  base.ax 60  c_CNE.p  L_C.ax L_GNE.ax
echo "# NE-collapse lemma (definitions only)"
step S1   base.ax 60  c_S1.p   none.ax
step S2pre base_ne_only.ax 60 c_S2pre.p
step S2a  base.ax 60  c_S2a.p  L_S1.ax L_S2pre.ax
step S2   base.ax 60  c_S2.p   L_S2a.ax
step NEMC base.ax 60  c_NEMC.p L_S2.ax
echo "# corollaries"
step MC   base.ax 60  c_MC.p   L_NEMC.ax L_CNE.ax
step NECG base.ax 60  c_T4.p   L_C.ax L_MC.ax
echo "# strengthened results (after review)"
step R1   base.ax 60  c_R1.p   none.ax                      # MC -> NE everywhere (converse)
step R2   base.ax 60  c_R2.p   A2.ax A5.ax L_NEMC.ax        # MC or every property positive
step R3   base.ax 60  c_MC.p   A2.ax A5.ax NoEmpty.ax L_NEMC.ax
step R4   base.ax 60  c_MC.p   L_T1.ax A5.ax L_NEMC.ax      # no A3 needed for MC
step R5   base.ax 60  c_R5.p   none.ax                      # complete concept is an essence
step EQV  base.ax 60  c_EQV.p  none.ax                      # opaque defs entail lambda defs
