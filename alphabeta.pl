:- use_module(library(lists)).
:- use_module(library(pairs)).

:- ensure_loaded('utility.pl').
:- ensure_loaded('moves.pl').
:- ensure_loaded('capture.pl').

:- dynamic tt_entry/4.

clear_tt :- retractall(tt_entry(_, _, _, _)).

board_hash(State, Hash) :-
    state_board(State, Board),
    state_player(State, Player),
    term_hash(Board-Player, Hash).

% ==========================================================
% List Trimmer for Beam Search
% ==========================================================
take(0, _, []) :- !.
take(_, [], []) :- !.
take(N, [H|T], [H|Rest]) :-
    N > 0,
    N1 is N - 1,
    take(N1, T, Rest).

% ==========================================================
% Move Ordering
% ==========================================================
order_moves(_, _, [], _, []).
order_moves(Board, Player, Moves, PrevBest, Ordered) :-
    ( PrevBest \= none, member(PrevBest, Moves) ->
        delete(Moves, PrevBest, Rest),
        score_and_sort(Board, Player, Rest, Sorted),
        Ordered = [PrevBest | Sorted]
    ;
        score_and_sort(Board, Player, Moves, Ordered)
    ).

score_and_sort(Board, Player, Moves, Ordered) :-
    maplist(score_move(Board, Player), Moves, Scored),
    msort(Scored, Sorted),
    reverse(Sorted, Desc),
    pairs_values(Desc, Ordered).

score_move(Board, defender, Move, Score-Move) :-
    Move = move(R1, C1, R2, C2),
    get_cell(Board, R1, C1, Piece),
    ( Piece == king ->
        ( corner(R2, C2) -> Score = 10000
        ; distance_to_best_corner(R2, C2, D), Score is 5000 - (D * 100)
        )
    ;
        ( would_capture(Board, defender, R2, C2) -> Score = 1000 ; Score = 0 )
    ).

score_move(Board, attacker, Move, Score-Move) :-
    Move = move(_, _, R2, C2),
    ( would_capture(Board, attacker, R2, C2) -> Score = 1000
    ;
        find_king(Board, 0, KR, KC),
        Dist is abs(R2 - KR) + abs(C2 - KC),
        Score is 100 - Dist
    ).

would_capture(Board, Player, R, C) :-
    direction(DR, DC),
    CapR is R + DR, CapC is C + DC,
    between(0, 10, CapR), between(0, 10, CapC),
    get_cell(Board, CapR, CapC, Enemy),
    enemy(Player, Enemy),
    OppR is CapR + DR, OppC is CapC + DC,
    between(0, 10, OppR), between(0, 10, OppC),
    get_cell(Board, OppR, OppC, Anvil),
    is_anvil(Player, Anvil, OppR, OppC), !.

% ==========================================================
% Iterative Deepening & Alpha-Beta
% ==========================================================
alphabeta_id(State, MaxDepth, Player, BestMove, BestValue) :-
    clear_tt,
    alphabeta_id_loop(State, 1, MaxDepth, Player, none, 0, BestMove, BestValue).

alphabeta_id_loop(_, Depth, MaxDepth, _, Move, Val, Move, Val) :-
    Depth > MaxDepth, !.

alphabeta_id_loop(State, Depth, MaxDepth, Player, PrevMove, _, FinalMove, FinalVal) :-
    alphabeta(State, Depth, -100000, 100000, Player, PrevMove, Move, Val),
    Next is Depth + 1,
    alphabeta_id_loop(State, Next, MaxDepth, Player, Move, Val, FinalMove, FinalVal).

alphabeta(State, 0, _, _, _, _, none, Value) :-
    evaluate_state(State, Value), !.

alphabeta(State, Depth, _, _, _, _, none, Value) :-
    check_winner(State, _), !,
    evaluate_state(State, Value).

alphabeta(State, Depth, Alpha, Beta, Player, PrevBest, BestMove, Value) :-
    board_hash(State, Hash),

    ( tt_entry(Hash, StoredDepth, exact, Stored), StoredDepth >= Depth ->
        Value = Stored, BestMove = none
    ;
        ( tt_entry(Hash, SD1, lower_bound, LB), SD1 >= Depth -> Alpha1 is max(Alpha, LB) ; Alpha1 = Alpha ),
        ( tt_entry(Hash, SD2, upper_bound, UB), SD2 >= Depth -> Beta1 is min(Beta, UB) ; Beta1 = Beta ),

        ( Alpha1 >= Beta1 ->
            Value = Alpha1, BestMove = none
        ;
            state_board(State, Board),
            findall(Move,
                ( nth0(Index, Board, Piece),
                  owns(Player, Piece),
                  R is Index // 11,
                  C is Index mod 11,
                  generate_piece_moves(Board, Player, Piece, R, C, Move)
                ),
            Moves),

            ( Moves == [] ->
                evaluate_state(State, Value), BestMove = none
            ;
                order_moves(Board, Player, Moves, PrevBest, OrderedAll),
                
                take(10, OrderedAll, Ordered),
                
                next_player(Player, Next),

                ( Player == defender ->
                    maximize(Ordered, State, Depth, Alpha1, Beta1, Next, none, -100000, BestMove, Value)
                ;
                    minimize(Ordered, State, Depth, Alpha1, Beta1, Next, none, 100000, BestMove, Value)
                ),

                ( Value =< Alpha1 -> Flag = upper_bound
                ; Value >= Beta1 -> Flag = lower_bound
                ; Flag = exact
                ),
                ( \+ tt_entry(Hash, _, _, _) ->
                    assertz(tt_entry(Hash, Depth, Flag, Value))
                ; true )
            )
        )
    ).

generate_piece_moves(Board, Player, Piece, R, C, move(R, C, R2, C2)) :-
    direction(DR, DC),
    slide_fast(Board, Piece, R, C, DR, DC, R2, C2),
    \+ is_suicide_move(Board, Player, Piece, R2, C2).

slide_fast(Board, Piece, R, C, DR, DC, R2, C2) :-
    NR is R + DR,
    NC is C + DC,
    between(0,10,NR),
    between(0,10,NC),
    get_cell(Board, NR, NC, empty),
    can_enter(Piece, NR, NC),
    (
        R2 = NR, C2 = NC
    ;
        slide_fast(Board, Piece, NR, NC, DR, DC, R2, C2)
    ).

maximize([], _, _, _, _, _, Move, Val, Move, Val).
maximize([Move|Rest], State, Depth, Alpha, Beta, Next, BestM, BestV, FinalM, FinalV) :-
    apply_move(State, Move, S2),
    D1 is Depth - 1,
    alphabeta(S2, D1, Alpha, Beta, Next, none, _, Val),
    ( Val > BestV ->
        M1 = Move, V1 = Val
    ;
        M1 = BestM, V1 = BestV
    ),
    ( V1 >= Beta ->
        FinalM = M1, FinalV = V1
    ;
        A1 is max(Alpha, V1),
        maximize(Rest, State, Depth, A1, Beta, Next, M1, V1, FinalM, FinalV)
    ).

minimize([], _, _, _, _, _, Move, Val, Move, Val).
minimize([Move|Rest], State, Depth, Alpha, Beta, Next, BestM, BestV, FinalM, FinalV) :-
    apply_move(State, Move, S2),
    D1 is Depth - 1,
    alphabeta(S2, D1, Alpha, Beta, Next, none, _, Val),
    ( Val < BestV ->
        M1 = Move, V1 = Val
    ;
        M1 = BestM, V1 = BestV
    ),
    ( V1 =< Alpha ->
        FinalM = M1, FinalV = V1
    ;
        B1 is min(Beta, V1),
        minimize(Rest, State, Depth, Alpha, B1, Next, M1, V1, FinalM, FinalV)
    ).