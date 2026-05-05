:- set_prolog_flag(stack_limit, 4_294_967_296).

:- ensure_loaded('board.pl').
:- ensure_loaded('moves.pl').
:- ensure_loaded('capture.pl').
:- ensure_loaded('alphabeta.pl').

:- dynamic current_state/1.

% ------------------------------------------------------------------
% Python Communication Interface
% ------------------------------------------------------------------

% init_game
% Initializes or resets the game state for Python and stores it.
init_game :-
    retractall(current_state(_)),
    initial_state(State),
    assertz(current_state(State)),
    flush_output.

% make_move(+R1, +C1, +R2, +C2)
% Validates and applies a move for the current player, updating state.
make_move(R1, C1, R2, C2) :-
    current_state(State),
    state_player(State, Player),
    Move = move(R1, C1, R2, C2),
    valid_move(State, Player, Move),
    apply_move(State, Move, NextState),
    retractall(current_state(_)),
    assertz(current_state(NextState)),
    flush_output.

% print_board_python
% Prints the current board as 11 comma-separated rows.
print_board_python :-
    current_state(State),
    state_board(State, Board),
    print_board_python(Board),
    flush_output.

% print_valid_moves(+Row, +Col)
% Outputs valid destinations as "R-C,R-C,..." or "none".
print_valid_moves(Row, Col) :-
    current_state(State),
    state_player(State, Player),
    findall(row_col(R2, C2),
            valid_move(State, Player, move(Row, Col, R2, C2)),
            Moves),
    ( Moves == [] ->
        write('none')
    ;
        write_moves_python(Moves)
    ),
    nl,
    flush_output.

write_moves_python([row_col(R, C)]) :-
    format('~w-~w', [R, C]).
write_moves_python([row_col(R, C)|Rest]) :-
    format('~w-~w,', [R, C]),
    write_moves_python(Rest).

% ai_make_move(+Depth)
% Uses alphabeta_id to pick and apply a move for the current player.
ai_make_move(Depth) :-
    current_state(State),
    state_player(State, Player),
    alphabeta_id(State, Depth, Player, BestMove, _Score),
    BestMove \= none,
    apply_move(State, BestMove, NextState),
    retractall(current_state(_)),
    assertz(current_state(NextState)),
    flush_output.

% current_turn(-Player)
% Writes attacker/defender for Python to read.
current_turn(Player) :-
    current_state(State),
    state_player(State, Player),
    write(Player), nl,
    flush_output.

% game_status(-Status)
% Writes ongoing, attacker_wins, or defender_wins.
game_status(Status) :-
    ( current_state(State), check_winner(State, Winner) ->
        ( Winner == attacker -> Status = attacker_wins
        ; Status = defender_wins
        )
    ;
        Status = ongoing
    ),
    write(Status), nl,
    flush_output.

% main_loop
% Reads terms from stdin, executes, writes SUCCESS/FAILED, loops until quit.
main_loop :-
    read(Term),
    ( Term == quit ->
        write('SUCCESS'), nl, flush_output
    ;
        ( call(Term) -> write('SUCCESS') ; write('FAILED') ),
        nl, flush_output,
        main_loop
    ).

% ------------------------------------------------------------------
% Internal helpers
% ------------------------------------------------------------------

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
