:- ensure_loaded('board.pl').
:- ensure_loaded('capture.pl').

owns(attacker, attacker).
owns(defender, defender).
owns(defender, king).

enemy(attacker, defender).
enemy(attacker, king).
enemy(defender, attacker).

direction(-1, 0).
direction(1, 0).
direction(0, -1).
direction(0, 1).

% valid_move(+State, +Player, -Move)
valid_move(state(Board, Player, _, _), Player, move(R1, C1, R2, C2)) :-
    owns(Player, TargetPiece),
    between(0, 10, R1),
    between(0, 10, C1),
    get_cell(Board, R1, C1, TargetPiece),
    direction(DR, DC),
    slide(Board, TargetPiece, R1, C1, DR, DC, R2, C2),
    \+ is_suicide_move(Board, Player, TargetPiece, R2, C2).

is_suicide_move(Board, Player, Piece, R, C) :-
    Piece \= king,
    (
        % Horizontal sandwich
        ( C1 is C - 1, C2 is C + 1,
          between(0, 10, C1), between(0, 10, C2),
          get_cell(Board, R, C1, Cell1), is_hostile(Player, Cell1, R, C1),
          get_cell(Board, R, C2, Cell2), is_hostile(Player, Cell2, R, C2)
        )
    ;
        % Vertical sandwich
        ( R1 is R - 1, R2 is R + 1,
          between(0, 10, R1), between(0, 10, R2),
          get_cell(Board, R1, C, Cell3), is_hostile(Player, Cell3, R1, C),
          get_cell(Board, R2, C, Cell4), is_hostile(Player, Cell4, R2, C)
        )
    ).

is_hostile(Player, Cell, _, _) :- enemy(Player, Cell).
is_hostile(_, empty, R, C) :- corner(R, C).
is_hostile(_, empty, R, C) :- throne(R, C).

% slide/8 recursively finds empty squares to slide into.
slide(Board, Piece, R, C, DR, DC, FinalR, FinalC) :-
    NextR is R + DR,
    NextC is C + DC,
    between(0, 10, NextR),
    between(0, 10, NextC),
    get_cell(Board, NextR, NextC, empty),
    can_enter(Piece, NextR, NextC),
    (
        FinalR = NextR, FinalC = NextC
    ;
        slide(Board, Piece, NextR, NextC, DR, DC, FinalR, FinalC)
    ).

% Only the King can access the Throne or Corners.
can_enter(king, _, _).
can_enter(Piece, R, C) :-
    Piece \= king,
    \+ throne(R, C),
    \+ corner(R, C).

% apply_move(+State, +Move, -NewState)
apply_move(state(Board, Player, A, D), move(R1, C1, R2, C2), state(NewBoard, NextPlayer, NewA, NewD)) :-
    get_cell(Board, R1, C1, Piece),
    set_cell(Board, R1, C1, empty, TempBoard1),
    set_cell(TempBoard1, R2, C2, Piece, TempBoard2),
    check_captures(TempBoard2, Player, R2, C2, NewBoard, CapsCount),
    next_player(Player, NextPlayer),
    (Player == attacker ->
        NewA = A, NewD is D - CapsCount
    ;
        NewA is A - CapsCount, NewD = D
    ).
