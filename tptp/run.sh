#!/bin/bash
# usage: run.sh <axiom files...> -- <conjecture file> [timeout]
LEO="../tools/leo3.jar"
ax=(); while [ "$1" != "--" ]; do ax+=("$1"); shift; done; shift
conj=$1; to=${2:-30}
mkdir -p work; f=work/$(echo "${ax[*]}" | tr ' ./' '___')_$(basename "$conj" .p).p
cat base.ax "${ax[@]}" "$conj" > "$f"
res=$(timeout $((to+20)) java -jar $LEO "$f" -t $to 2>&1 | grep -o "SZS status [A-Za-z]*" | head -1)
echo "${ax[*]} | $conj | ${res:-NO_ANSWER}"
