:- ensure_loaded('board.pl').
:- ensure_loaded('moves.pl').
:- ensure_loaded('capture.pl').

% evaluate_state(+State, -Score)
% Evaluates the game state from the Defender's perspective (+ is good for Defender).
% Win condition checks take top precedence.
evaluate_state(State, Score) :-
    check_winner(State, Winner), !,
    ( Winner == defender -> Score = 10000
    ; Score = -10000
    ).
evaluate_state(state(Board, _, A, D), Score) :-
    find_king(Board, 0, KR, KC),
    
    % 1. King's distance to best corner
    distance_to_best_corner(KR, KC, Dist),
    
    % 2. Material Advantage
    Material is (D * 10) - (A * 5),
    
    % 3. Potential King Encirclement penalty
    encirclement_penalty(Board, KR, KC, Penalty),
    
    % 4. Open free escape routes to corners
    open_escape_routes(Board, KR, KC, Routes),
    
    Score is Material - (Dist * 10) - (Penalty * 15) + (Routes * 50).

% Manhattan distance to the closest corner
distance_to_best_corner(KR, KC, MinDist) :-
    findall(D, (corner(CR, CC), D is abs(KR - CR) + abs(KC - CC)), Distances),
    min_list(Distances, MinDist).

% Counts how many immediately neighboring spots are hostile
encirclement_penalty(Board, KR, KC, Penalty) :-
    findall(1, (direction(DR, DC), AdjR is KR + DR, AdjC is KC + DC,
                hostile_to_king(Board, AdjR, AdjC)), Hostiles),
    sum_list(Hostiles, Penalty).

% Checks path availability from King to any corner (a straight-line shot like an unobstructed Rook)
open_escape_routes(Board, KR, KC, Routes) :-
    findall(1, (corner(CR, CC), is_open_path(Board, KR, KC, CR, CC)), OpenPaths),
    sum_list(OpenPaths, Routes).

% Returns true if there exists a complete straight (orthogonal) line of empty squares to a corner.
is_open_path(Board, KR, KC, CR, CC) :-
    KR =:= CR, path_empty(Board, KR, KC, CR, CC), !.
is_open_path(Board, KR, KC, CR, CC) :-
    KC =:= CC, path_empty(Board, KR, KC, CR, CC), !.

path_empty(_, R, C, R, C) :- !.
path_empty(Board, R1, C, R2, C) :- R1 < R2, R is R1 + 1, all_empty_col(Board, R, R2, C).
path_empty(Board, R1, C, R2, C) :- R1 > R2, R is R1 - 1, all_empty_col(Board, R, R2, C).
path_empty(Board, R, C1, R, C2) :- C1 < C2, C is C1 + 1, all_empty_row(Board, R, C, C2).
path_empty(Board, R, C1, R, C2) :- C1 > C2, C is C1 - 1, all_empty_row(Board, R, C, C2).

all_empty_col(_, TargetR, TargetR, _) :- !.
all_empty_col(Board, CurrR, TargetR, C) :-
    CurrR < TargetR,
    get_cell(Board, CurrR, C, Cell),
    (Cell == empty ; throne(CurrR, C)),
    NextR is CurrR + 1, all_empty_col(Board, NextR, TargetR, C).
all_empty_col(Board, CurrR, TargetR, C) :-
    CurrR > TargetR,
    get_cell(Board, CurrR, C, Cell),
    (Cell == empty ; throne(CurrR, C)),
    NextR is CurrR - 1, all_empty_col(Board, NextR, TargetR, C).

all_empty_row(_, _, TargetC, TargetC) :- !.
all_empty_row(Board, R, CurrC, TargetC) :-
    CurrC < TargetC,
    get_cell(Board, R, CurrC, Cell),
    (Cell == empty ; throne(R, CurrC)),
    NextC is CurrC + 1, all_empty_row(Board, R, NextC, TargetC).
all_empty_row(Board, R, CurrC, TargetC) :-
    CurrC > TargetC,
    get_cell(Board, R, CurrC, Cell),
    (Cell == empty ; throne(R, CurrC)),
    NextC is CurrC - 1, all_empty_row(Board, R, NextC, TargetC).