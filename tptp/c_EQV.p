%  opaque definitions entail the lambda definitions (so mixing encodings is sound)
thf(eqv, conjecture, (g = (^[X:$i, W:w]: ![Phi:$i>w>$o]: ((p @ Phi @ W) => (Phi @ X @ W)))) & (ess = (^[Phi:$i>w>$o, X:$i, W:w]: ((Phi @ X @ W) & ![Psi:$i>w>$o]: ((Psi @ X @ W) => ![V:w, Y:$i]: ((Phi @ Y @ V) => (Psi @ Y @ V))))))).
