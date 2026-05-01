:- ensure_loaded('board.pl').
:- ensure_loaded('moves.pl').
:- ensure_loaded('capture.pl').
:- ensure_loaded('alphabeta.pl').

% Difficulty mapping: Easy = 1, Medium = 3, Hard = 5
set_difficulty(1, 1). 
set_difficulty(2, 3). 
set_difficulty(3, 5). 

start :-
    write('--- HNEFATAFL: Viking Chess ---'), nl,
    write('Select game mode:'), nl,
    write('1. Human vs Computer'), nl,
    write('2. Human vs Human'), nl,
    write('Choice (end with dot .): '),
    read(ModeChoice),
    initial_state(State),
    ( ModeChoice == 2 ->
        write('Starting Human vs Human mode...'), nl,
        game_loop_hvh(State)
    ;
        write('Select difficulty: 1 (Easy), 2 (Medium), 3 (Hard).'), nl,
        write('Choice (end with dot .): '),
        read(DiffChoice),
        set_difficulty(DiffChoice, Depth),
        write('Do you want to play as attacker (a) or defender (d)?'), nl,
        write('Choice (end with dot .): '),
        read(RoleChoice),
        ( RoleChoice == a -> Human = attacker, AI = defender
        ; Human = defender, AI = attacker
        ),
        write('Starting Human vs Computer mode...'), nl,
        game_loop_hvc(State, Human, AI, Depth)
    ).

% Shared End Game State Check
check_game_over(State) :-
    check_winner(State, Winner), !,
    state_board(State, Board),
    print_board(Board),
    nl, write('=============================='), nl,
    format(' END OF GAME: The ~w wins!~n', [Winner]),
    write('=============================='), nl.

% ---------------------------------------------
% Human vs Human Loop
% ---------------------------------------------
game_loop_hvh(State) :-
    check_game_over(State), !.
game_loop_hvh(State) :-
    state_player(State, Current),
    state_board(State, Board),
    print_board(Board),
    format('~nCurrent turn: ~w~n', [Current]),
    human_turn(State, Current, NextState),
    game_loop_hvh(NextState).

% ---------------------------------------------
% Human vs Computer Loop
% ---------------------------------------------
game_loop_hvc(State, _, _, _) :-
    check_game_over(State), !.
game_loop_hvc(State, Human, AI, Depth) :-
    state_player(State, Current),
    state_board(State, Board),
    print_board(Board),
    format('~nCurrent turn: ~w~n', [Current]),
    ( Current == Human ->
        human_turn(State, Human, NextState)
    ;
        ai_turn(State, AI, Depth, NextState)
    ),
    game_loop_hvc(NextState, Human, AI, Depth).

% ---------------------------------------------
% Turn Helpers
% ---------------------------------------------
human_turn(State, Player, NextState) :-
    write('Enter your move as R1. C1. R2. C2. (e.g., 0. 3. 0. 2.)'), nl,
    write('Row 1: '), read(R1),
    write('Col 1: '), read(C1),
    write('Row 2: '), read(R2),
    write('Col 2: '), read(C2),
    Move = move(R1, C1, R2, C2),
    ( valid_move(State, Player, Move) ->
        apply_move(State, Move, NextState),
        write('Move accepted.'), nl
    ;
        write('Invalid move! Please check your coordinates and ensure the path is clear.'), nl,
        human_turn(State, Player, NextState)
    ).

ai_turn(State, AI, Depth, NextState) :-
    write('Computer is calculating the best move...'), nl,
    alphabeta(State, Depth, -100000, 100000, AI, BestMove, _Score),
    ( BestMove == none -> 
        % Fallback if AI gets completely trapped before end-state registers
        write('Computer has no valid moves. Human wins!'), nl, abort
    ;
        BestMove = move(R1, C1, R2, C2),
        format('Computer plays: (~w, ~w) -> (~w, ~w)~n', [R1, C1, R2, C2]),
        apply_move(State, BestMove, NextState)
    ).