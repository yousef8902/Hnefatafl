:- ensure_loaded('utility.pl').
:- ensure_loaded('moves.pl').
:- ensure_loaded('capture.pl').

% alphabeta(+State, +Depth, +Alpha, +Beta, +Player, -BestMove, -BestValue)
% Base cases: Depth 0 or terminal state
alphabeta(State, 0, _, _, _, none, Value) :-
    evaluate_state(State, Value), !.

alphabeta(State, _, _, _, _, none, Value) :-
    check_winner(State, _), !,
    evaluate_state(State, Value).

% Recursive case
alphabeta(State, Depth, Alpha, Beta, Player, BestMove, Value) :-
    findall(Move, valid_move(State, Player, Move), Moves),
    ( Moves == [] -> 
        evaluate_state(State, Value), BestMove = none
    ; 
        next_player(Player, NextPlayer),
        ( Player == defender -> 
            % Defender maximizes the score
            maximize(Moves, State, Depth, Alpha, Beta, NextPlayer, none, -100000, BestMove, Value)
        ; 
            % Attacker minimizes the score
            minimize(Moves, State, Depth, Alpha, Beta, NextPlayer, none, 100000, BestMove, Value)
        )
    ).

% maximize(+Moves, +State, +Depth, +Alpha, +Beta, +NextPlayer, +RecordMove, +RecordVal, -BestMove, -BestVal)
maximize([], _, _, _, _, _, BestMove, BestVal, BestMove, BestVal).
maximize([Move|Rest], State, Depth, Alpha, Beta, NextPlayer, RecordMove, RecordVal, BestMove, BestVal) :-
    apply_move(State, Move, NextState),
    D1 is Depth - 1,
    alphabeta(NextState, D1, Alpha, Beta, NextPlayer, _, Val),
    ( Val > RecordVal -> NewRecordVal = Val, NewRecordMove = Move ; NewRecordVal = RecordVal, NewRecordMove = RecordMove ),
    ( NewRecordVal >= Beta -> 
        BestMove = NewRecordMove, BestVal = NewRecordVal % Beta cutoff
    ; 
        NewAlpha is max(Alpha, NewRecordVal),
        maximize(Rest, State, Depth, NewAlpha, Beta, NextPlayer, NewRecordMove, NewRecordVal, BestMove, BestVal)
    ).

% minimize(+Moves, +State, +Depth, +Alpha, +Beta, +NextPlayer, +RecordMove, +RecordVal, -BestMove, -BestVal)
minimize([], _, _, _, _, _, BestMove, BestVal, BestMove, BestVal).
minimize([Move|Rest], State, Depth, Alpha, Beta, NextPlayer, RecordMove, RecordVal, BestMove, BestVal) :-
    apply_move(State, Move, NextState),
    D1 is Depth - 1,
    alphabeta(NextState, D1, Alpha, Beta, NextPlayer, _, Val),
    ( Val < RecordVal -> NewRecordVal = Val, NewRecordMove = Move ; NewRecordVal = RecordVal, NewRecordMove = RecordMove ),
    ( NewRecordVal =< Alpha -> 
        BestMove = NewRecordMove, BestVal = NewRecordVal % Alpha cutoff
    ; 
        NewBeta is min(Beta, NewRecordVal),
        minimize(Rest, State, Depth, Alpha, NewBeta, NextPlayer, NewRecordMove, NewRecordVal, BestMove, BestVal)
    ).