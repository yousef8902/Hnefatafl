import threading
from copy import deepcopy

from .prolog_bridge import PrologBridge


class GameController:
    def __init__(self, prolog_file):
        self.bridge = PrologBridge(prolog_file)
        self.board = []
        self.current_turn = "attacker"
        self.status = "ongoing"
        self._ai_thread = None
        self.ai_thinking = False
        self._last_move_lock = threading.Lock()
        self._last_move_info = None

    def close(self):
        self.bridge.close()

    def start_game(self):
        self.bridge.query_lines("init_game")
        self.sync_board()
        self.current_turn = self._read_turn()
        self.status = self._read_status()
        with self._last_move_lock:
            self._last_move_info = None

    def sync_board(self):
        # Prolog prints 11 comma-separated rows; parse into a 2D list.
        lines = self.bridge.query_lines("print_board_python")
        if len(lines) != 11:
            raise RuntimeError("Invalid board output from Prolog")
        self.board = [row.split(",") for row in lines]

    def make_move(self, r1, c1, r2, c2):
        prev_board = deepcopy(self.board)
        self.bridge.query_lines(f"make_move({r1},{c1},{r2},{c2})")
        self.sync_board()
        self.current_turn = self._read_turn()
        self.status = self._read_status()
        move_info = self._compute_move_delta(prev_board, self.board)
        return move_info

    def get_valid_moves(self, row, col):
        line = self.bridge.query_single_line(f"print_valid_moves({row},{col})")
        if line == "none" or line == "":
            return []
        moves = []
        for part in line.split(","):
            r_str, c_str = part.split("-")
            moves.append((int(r_str), int(c_str)))
        return moves

    def start_ai_move(self, depth):
        if self.ai_thinking:
            return

        self.ai_thinking = True

        def worker():
            try:
                prev_board = deepcopy(self.board)
                self.bridge.query_lines(f"ai_make_move({depth})")
                self.sync_board()
                self.current_turn = self._read_turn()
                self.status = self._read_status()
                move_info = self._compute_move_delta(prev_board, self.board)
                with self._last_move_lock:
                    self._last_move_info = move_info
            finally:
                self.ai_thinking = False

        self._ai_thread = threading.Thread(target=worker, daemon=True)
        self._ai_thread.start()

    def consume_last_move(self):
        with self._last_move_lock:
            info = self._last_move_info
            self._last_move_info = None
        return info

    def _read_turn(self):
        return self.bridge.query_single_line("current_turn(Player)")

    def _read_status(self):
        return self.bridge.query_single_line("game_status(Status)")

    def count_pieces(self):
        attackers = 0
        defenders = 0
        king = 0
        for row in self.board:
            for cell in row:
                if cell == "a":
                    attackers += 1
                elif cell == "d":
                    defenders += 1
                elif cell == "k":
                    king += 1
        return attackers, defenders, king

    def _compute_move_delta(self, prev_board, next_board):
        from_pos = None
        to_pos = None
        captures = []

        for r in range(len(prev_board)):
            for c in range(len(prev_board[r])):
                before = prev_board[r][c]
                after = next_board[r][c]
                if before == "e" and after != "e":
                    to_pos = (r, c)

        if to_pos is None:
            return None

        piece = next_board[to_pos[0]][to_pos[1]]

        for r in range(len(prev_board)):
            for c in range(len(prev_board[r])):
                before = prev_board[r][c]
                after = next_board[r][c]
                if before != "e" and after == "e":
                    if before == piece and from_pos is None:
                        from_pos = (r, c)
                    else:
                        captures.append((r, c, before))

        if from_pos is None:
            return None

        side = "attacker" if piece == "a" else "defender"
        notation = self._format_move_notation(from_pos, to_pos, captures)
        return {
            "from": from_pos,
            "to": to_pos,
            "piece": piece,
            "captures": captures,
            "side": side,
            "notation": notation,
        }

    def _format_move_notation(self, from_pos, to_pos, captures):
        letters = "abcdefghijk"
        r1, c1 = from_pos
        r2, c2 = to_pos
        start = f"{letters[c1]}{r1 + 1}"
        end = f"{letters[c2]}{r2 + 1}"
        capture_tag = "x" if captures else ""
        return f"{start}-{end}{capture_tag}"
