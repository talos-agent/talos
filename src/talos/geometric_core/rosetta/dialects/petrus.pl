% Fatos: Ângulos de Bragg
phase(claude, 0.0).
phase(gemini, 1.047). % pi/3

% Regra: Interferência Construtiva se diferença < limiar
constructive(NodeA, NodeB) :-
    phase(NodeA, P1),
    phase(NodeB, P2),
    Diff is abs(P1 - P2),
    Diff < 0.78. % pi/4
