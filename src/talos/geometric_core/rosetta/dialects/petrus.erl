-module(petrus).
-export([start_node/1, loop/1]).

loop(MyPhase) ->
    receive
        {interfere, From, OtherPhase} ->
            Delta = math:cos(abs(MyPhase - OtherPhase)),
            From ! {result, Delta},
            loop(MyPhase)
    end.
