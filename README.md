# Hnefatafl
An implementation of the strategy game Hnefatafl, built as part of the CS361 Artificial Intelligence course at Cairo University. The Prolog backend owns all game rules and AI, while a Python/Pygame GUI provides the user interface.

## Project Structure
- Prolog backend:
	- alphabeta.pl
	- board.pl
	- capture.pl
	- controller.pl
	- moves.pl
	- utility.pl
- Python GUI:
	- hnefatafl/main.py
	- hnefatafl/game_controller.py
	- hnefatafl/prolog_bridge.py
	- hnefatafl/constants.py
	- hnefatafl/gui/renderer.py
	- hnefatafl/gui/input_handler.py

## Requirements
- SWI-Prolog (swipl)
- Python 3.12+
- pygame

## Install
From the repository root:
```
python -m pip install pygame
```

## Run
From the repository root:
```
python -m hnefatafl.main
```

If `swipl` is not in PATH, install SWI-Prolog and add it to PATH. The GUI launches Prolog using:
```
swipl -q -f controller.pl -g main_loop
```

## Game Overview
- Board size: 11x11
- Attackers: 24 black soldiers
- Defenders: 12 white soldiers + 1 king
- Attackers move first
- Pieces move like a chess rook (any number of squares orthogonally)
- Captures are custodial (sandwiching between two opposing pieces)
- Defender wins if the king reaches any corner
- Attacker wins by surrounding the king on all available sides

## Features
- Difficulty selection: Easy (depth 1), Medium (depth 3), Hard (depth 5)
- Human plays defender, AI plays attacker
- Corner and throne highlights
- Valid-move previews
- Non-blocking AI ("Thinking..." overlay)
- Win/loss popup with restart

## Controls
- Start screen: select difficulty (Easy/Medium/Hard)
- Click to select a defender or king, then click a valid destination

## Prolog Communication Protocol
Python communicates with SWI-Prolog over stdin/stdout:
- Each query is sent as a Prolog term ending with a period
- Prolog responds with data lines (if any) and then a final line:
	- SUCCESS
	- FAILED
- Prolog flushes output after every response to avoid blocking

### Prolog Predicates Used by Python
- init_game
	- Resets the game state
- print_board_python
	- Prints 11 comma-separated rows using: a, d, k, e
- make_move(R1, C1, R2, C2)
	- Applies a move for the current player
- print_valid_moves(Row, Col)
	- Prints destinations as "R-C,R-C,..." or "none"
- ai_make_move(Depth)
	- Computes and applies the best move
- current_turn(Player)
	- Writes attacker or defender
- game_status(Status)
	- Writes ongoing, attacker_wins, defender_wins
- main_loop
	- Reads terms from stdin and executes them

## Troubleshooting
- `ModuleNotFoundError: pygame`
	- Run: `python -m pip install pygame`
- `swipl` not found
	- Install SWI-Prolog and add it to PATH, or update the launcher in the Python bridge
- GUI opens but no moves show
	- Ensure Prolog launches successfully; check the terminal output

## Notes
- The GUI is non-blocking; it shows a "Thinking..." overlay while the AI computes.
- All game rules live in Prolog; Python only renders and forwards moves.
