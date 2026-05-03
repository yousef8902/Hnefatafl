# Hnefatafl
An implementation of the strategy game Hnefatafl, built as part of the CS361 Artificial Intelligence course at Cairo University. The Prolog backend handles all game rules and AI, while a Python/Pygame GUI provides the user interface.

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
python.exe -m pip install pygame
```

## Run
From the repository root:
```
python.exe -m hnefatafl.main
```

If `swipl` is not in PATH, install SWI-Prolog and add it to PATH. The GUI launches Prolog using:
```
swipl -q -f controller.pl -g main_loop
```

## Controls
- Start screen: select difficulty (Easy/Medium/Hard)
- Human plays defender (white) and moves by click-to-select, click-to-move
- AI plays attacker (black)

## Notes
- The GUI is non-blocking; it shows a "Thinking..." overlay while the AI computes.
- All game rules live in Prolog; Python only renders and forwards moves.
