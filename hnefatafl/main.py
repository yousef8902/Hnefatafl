import os
import sys

import pygame

from .constants import (
    BOARD_ORIGIN,
    BOARD_PIXELS,
    BUTTON_GAP,
    BUTTON_HEIGHT,
    BUTTON_WIDTH,
    CELL_SIZE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from .game_controller import GameController
from .gui.input_handler import pos_to_cell
from .gui.renderer import Renderer


def build_start_buttons():
    total_height = BUTTON_HEIGHT * 3 + BUTTON_GAP * 2
    start_y = 220
    start_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
    buttons = {}
    labels = ["Easy", "Medium", "Hard"]
    for i, label in enumerate(labels):
        y = start_y + i * (BUTTON_HEIGHT + BUTTON_GAP)
        buttons[label] = pygame.Rect(start_x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
    return buttons


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Hnefatafl")
    clock = pygame.time.Clock()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    gui_bridge = os.path.normpath(os.path.join(base_dir, "..", "gui_bridge.pl"))
    default_controller = os.path.normpath(os.path.join(base_dir, "..", "controller.pl"))
    prolog_file = gui_bridge if os.path.exists(gui_bridge) else default_controller

    renderer = Renderer()
    controller = GameController(prolog_file)

    state = "start"
    selected = None
    valid_moves = []
    ai_depth = 1
    restart_button = pygame.Rect(
        SCREEN_WIDTH // 2 - 120,
        SCREEN_HEIGHT // 2 - 10,
        240,
        54,
    )

    buttons = build_start_buttons()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if state == "start" and event.type == pygame.MOUSEBUTTONDOWN:
                for label, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        if label == "Easy":
                            ai_depth = 1
                        elif label == "Medium":
                            ai_depth = 3
                        else:
                            ai_depth = 5
                        controller.start_game()
                        state = "playing"
                        selected = None
                        valid_moves = []
                        if controller.current_turn == "attacker":
                            controller.start_ai_move(ai_depth)
                        break

            if state == "playing" and event.type == pygame.MOUSEBUTTONDOWN:
                if controller.ai_thinking or controller.status != "ongoing":
                    continue
                cell = pos_to_cell(event.pos)
                if cell is None:
                    continue
                row, col = cell
                piece = controller.board[row][col]

                if selected and (row, col) in valid_moves:
                    sr, sc = selected
                    controller.make_move(sr, sc, row, col)
                    selected = None
                    valid_moves = []
                    if controller.status == "ongoing" and controller.current_turn == "attacker":
                        controller.start_ai_move(ai_depth)
                elif piece in ("d", "k") and controller.current_turn == "defender":
                    selected = (row, col)
                    valid_moves = controller.get_valid_moves(row, col)
                else:
                    selected = None
                    valid_moves = []

            if state == "gameover" and event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    state = "start"

        if state == "playing" and controller.status != "ongoing":
            state = "gameover"

        renderer.draw_background(screen)

        if state == "start":
            renderer.draw_start_screen(screen, buttons)
        else:
            renderer.draw_board(screen, controller.board, selected, valid_moves)
            attackers, defenders, _king = controller.count_pieces()
            captured_attackers = 24 - attackers
            captured_defenders = 12 - defenders
            renderer.draw_status(screen, controller.current_turn, captured_attackers, captured_defenders)

            if controller.ai_thinking:
                renderer.draw_thinking_overlay(screen)

            if state == "gameover":
                winner = "Defender" if controller.status == "defender_wins" else "Attacker"
                renderer.draw_game_over(screen, winner, restart_button)

        pygame.display.flip()
        clock.tick(60)

    controller.close()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
