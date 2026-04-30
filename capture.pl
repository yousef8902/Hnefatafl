:- ensure_loaded('board.pl').
:- ensure_loaded('moves.pl').

% check_captures(+Board, +MoverPlayer, +R2, +C2, -NewBoard, -CapturedCount)
check_captures(Board, Player, R, C, FinalBoard, Count) :-
    findall(row_col(CapR, CapC),
            ( direction(DR, DC),
              captures_in_dir(Board, Player, R, C, DR, DC, CapR, CapC)
            ),
            Caps),
    length(Caps, Count),
    remove_pieces(Board, Caps, FinalBoard).

remove_pieces(Board, [], Board).
remove_pieces(Board, [row_col(R, C)|T], FinalBoard) :-
    set_cell(Board, R, C, empty, Temp),
    remove_pieces(Temp, T, FinalBoard).

% Checks if applying custodial capture is valid in a specific direction
captures_in_dir(Board, Player, R, C, DR, DC, CapR, CapC) :-
    CapR is R + DR, CapC is C + DC,
    between(0, 10, CapR), between(0, 10, CapC),
    get_cell(Board, CapR, CapC, EnemyPiece),
    enemy(Player, EnemyPiece),
    EnemyPiece \= king, % General piece capture (King is handled by encirclement)
    OppR is CapR + DR, OppC is CapC + DC,
    between(0, 10, OppR), between(0, 10, OppC),
    get_cell(Board, OppR, OppC, AnvilPiece),
    is_anvil(Player, AnvilPiece, OppR, OppC).

% Attacker anvils: another attacker, corner, or throne.
is_anvil(attacker, Piece, _, _) :- Piece == attacker.
is_anvil(attacker, _, R, C) :- corner(R, C).
is_anvil(attacker, _, R, C) :- throne(R, C).

% Defender anvils: another defender, corner, or throne. King is NOT an anvil.
is_anvil(defender, Piece, _, _) :- Piece == defender.
is_anvil(defender, _, R, C) :- corner(R, C).
is_anvil(defender, _, R, C) :- throne(R, C).

% check_winner(+State, -Winner)
check_winner(state(Board, _, _, _), defender) :-
    corner(R, C),
    get_cell(Board, R, C, king), !.

check_winner(state(Board, _, _, _), attacker) :-
    find_king(Board, 0, KR, KC),
    king_surrounded(Board, KR, KC), !.

find_king(Board, Row, KR, KC) :-
    Row < 11,
    ( find_king_in_row(Board, Row, 0, C) -> KR = Row, KC = C
    ; NextR is Row + 1, find_king(Board, NextR, KR, KC)
    ).

find_king_in_row(Board, Row, Col, KC) :-
    Col < 11,
    ( get_cell(Board, Row, Col, king) -> KC = Col
    ; NextC is Col + 1, find_king_in_row(Board, Row, NextC, KC)
    ).

% King is captured if all adjacent available sides are hostile.
king_surrounded(Board, KR, KC) :-
    forall(direction(DR, DC),
           ( AdjR is KR + DR, AdjC is KC + DC,
             hostile_to_king(Board, AdjR, AdjC)
           )).

% Defines squares/edges natively hostile to the King.
hostile_to_king(Board, R, C) :-
    ( \+ between(0, 10, R) % Wall (out of bounds)
    ; \+ between(0, 10, C) % Wall (out of bounds)
    ; get_cell(Board, R, C, attacker)
    ; corner(R, C)
    ; throne(R, C)
    ), !.