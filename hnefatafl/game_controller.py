import threading

from .prolog_bridge import PrologBridge


class GameController:
    def __init__(self, prolog_file):
        self.bridge = PrologBridge(prolog_file)
        self.board = []
        self.current_turn = "attacker"
        self.status = "ongoing"
        self._ai_thread = None
        self.ai_thinking = False

    def close(self):
        self.bridge.close()

    def start_game(self):
        self.bridge.query_lines("init_game")
        self.sync_board()
        self.current_turn = self._read_turn()
        self.status = self._read_status()

    def sync_board(self):
        # Prolog prints 11 comma-separated rows; parse into a 2D list.
        lines = self.bridge.query_lines("print_board_python")
        if len(lines) != 11:
            raise RuntimeError("Invalid board output from Prolog")
        self.board = [row.split(",") for row in lines]

    def make_move(self, r1, c1, r2, c2):
        self.bridge.query_lines(f"make_move({r1},{c1},{r2},{c2})")
        self.sync_board()
        self.current_turn = self._read_turn()
        self.status = self._read_status()

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
                self.bridge.query_lines(f"ai_make_move({depth})")
                self.sync_board()
                self.current_turn = self._read_turn()
                self.status = self._read_status()
            finally:
                self.ai_thinking = False

        self._ai_thread = threading.Thread(target=worker, daemon=True)
        self._ai_thread.start()

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
