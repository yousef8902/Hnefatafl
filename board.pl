%  Cell Types 
% empty       : empty square
% attacker    : black attacking piece
% defender    : white defending piece
% king        : the King piece
% throne      : center square (special, can be used in captures)
% corner      : corner squares (king's escape + capture aid)

% Special Squares 
corner(0,  0).
corner(0,  10).
corner(10, 0).
corner(10, 10).

throne(5, 5).

% Encoding helpers 

% pos_to_index(+Row, +Col, -Index)
pos_to_index(Row, Col, Index) :-
    Index is Row * 11 + Col.

% index_to_pos(+Index, -Row, -Col)
index_to_pos(Index, Row, Col) :-
    Row is Index // 11,
    Col is Index mod 11.

% get_cell(+Board, +Row, +Col, -Cell)
get_cell(Board, Row, Col, Cell) :-
    pos_to_index(Row, Col, Index),
    nth0(Index, Board, Cell).

% set_cell(+Board, +Row, +Col, +NewCell, -NewBoard)
set_cell(Board, Row, Col, NewCell, NewBoard) :-
    pos_to_index(Row, Col, Index),
    set_nth0(Index, Board, NewCell, NewBoard).

% Helper: replace element at index in a list
set_nth0(0, [_|T], NewElem, [NewElem|T]).
set_nth0(N, [H|T], NewElem, [H|T2]) :-
    N > 0,
    N1 is N - 1,
    set_nth0(N1, T, NewElem, T2).


% Initial Board Setup (11x11)

% Attacker positions (24 total, 4 groups of 6 around edges)
attacker_positions([
    % Top group
    row_col(0,3), row_col(0,4), row_col(0,5), row_col(0,6), row_col(0,7),
    row_col(1,5),
    % Bottom group
    row_col(10,3), row_col(10,4), row_col(10,5), row_col(10,6), row_col(10,7),
    row_col(9,5),
    % Left group
    row_col(3,0), row_col(4,0), row_col(5,0), row_col(6,0), row_col(7,0),
    row_col(5,1),
    % Right group
    row_col(3,10), row_col(4,10), row_col(5,10), row_col(6,10), row_col(7,10),
    row_col(5,9)
]).

% Defender positions (12 total, cross formation around king)
defender_positions([
    row_col(3,5), row_col(4,5),
    row_col(5,3), row_col(5,4),
    row_col(5,6), row_col(5,7),
    row_col(6,5), row_col(7,5),
    row_col(4,4), row_col(4,6),
    row_col(6,4), row_col(6,6)
]).

% King starts at throne (5,5)
king_position(row_col(5,5)).

% Build the initial board 

% Start with 121 empty cells, then place pieces.
initial_board(Board) :-
    length(EmptyBoard, 121),
    maplist(=(empty), EmptyBoard),
    king_position(row_col(KR, KC)),
    set_cell(EmptyBoard, KR, KC, king, B1),
    attacker_positions(Attackers),
    place_pieces(B1, Attackers, attacker, B2),
    defender_positions(Defenders),
    place_pieces(B2, Defenders, defender, Board).

% place_pieces(+Board, +PosList, +PieceType, -NewBoard)
place_pieces(Board, [], _, Board).
place_pieces(Board, [row_col(R,C)|Rest], Piece, FinalBoard) :-
    set_cell(Board, R, C, Piece, TmpBoard),
    place_pieces(TmpBoard, Rest, Piece, FinalBoard).

% Game State Representation
% state(Board, CurrentPlayer, AttackerCount, DefenderCount)
% CurrentPlayer: attacker | defender

initial_state(state(Board, attacker, 24, 12)) :-
    initial_board(Board).

% Accessors 
state_board(state(Board, _, _, _), Board).
state_player(state(_, Player, _, _), Player).
state_attackers(state(_, _, A, _), A).
state_defenders(state(_, _, _, D), D).

% Switch turn
next_player(attacker, defender).
next_player(defender, attacker).

% Board Printing

print_board(Board) :-
    nl,
    write('    0   1   2   3   4   5   6   7   8   9  10'), nl,
    write('  +---+---+---+---+---+---+---+---+---+---+---+'), nl,
    print_rows(Board, 0).

print_rows(_, 11) :- !.
print_rows(Board, Row) :-
    Row < 11,
    (Row < 10 -> format(' ~w|', [Row]) ; format('~w|', [Row])),
    print_cols(Board, Row, 0),
    nl,
    write('  +---+---+---+---+---+---+---+---+---+---+---+'), nl,
    Row1 is Row + 1,
    print_rows(Board, Row1).

print_cols(_, _, 11) :- !.
print_cols(Board, Row, Col) :-
    Col < 11,
    get_cell(Board, Row, Col, Cell),
    cell_symbol(Row, Col, Cell, Symbol),
    format(' ~w |', [Symbol]),
    Col1 is Col + 1,
    print_cols(Board, Row, Col1).

% Map cell type to display symbol
cell_symbol(_, _, king,     'K').
cell_symbol(_, _, attacker, 'A').
cell_symbol(_, _, defender, 'D').
cell_symbol(R, C, empty, 'C') :- corner(R, C), !.   % corner marker
cell_symbol(R, C, empty, 'T') :- throne(R, C), !.   % throne marker at center
cell_symbol(_, _, empty, ' ').

% Python-friendly board printing (11 lines, comma-separated)
% a = attacker, d = defender, k = king, e = empty
print_board_python(Board) :-
    print_python_rows(Board, 0).

print_python_rows(_, 11) :- !.
print_python_rows(Board, Row) :-
    Row < 11,
    print_python_cols(Board, Row, 0),
    nl,
    Row1 is Row + 1,
    print_python_rows(Board, Row1).

print_python_cols(_, _, 11) :- !.
print_python_cols(Board, Row, Col) :-
    Col < 11,
    get_cell(Board, Row, Col, Cell),
    python_cell_symbol(Cell, Symbol),
    ( Col == 0 -> write(Symbol) ; format(',~w', [Symbol]) ),
    Col1 is Col + 1,
    print_python_cols(Board, Row, Col1).

python_cell_symbol(attacker, 'a') :- !.
python_cell_symbol(defender, 'd') :- !.
python_cell_symbol(king, 'k') :- !.
python_cell_symbol(_, 'e').

%  Run: initialize and print (for testing)

run :-
    initial_state(State),
    state_board(State, Board),
    state_player(State, Player),
    print_board(Board),
    format('~nCurrent player: ~w~n', [Player]).