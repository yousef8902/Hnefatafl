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


def build_menu_buttons(labels, start_y=220):
    start_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
    buttons = {}
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

    state = "menu"
    selected = None
    valid_moves = []
    ai_depth = 1
    human_side = "defender"
    selected_difficulty = None
    selected_side = None
    restart_button = pygame.Rect(
        SCREEN_WIDTH // 2 - 120,
        SCREEN_HEIGHT // 2 - 10,
        240,
        54,
    )
    start_button = pygame.Rect(
        SCREEN_WIDTH // 2 - 120,
        640,
        240,
        54,
    )

    difficulty_buttons = build_menu_buttons(["Easy", "Medium", "Hard"], start_y=200)
    side_buttons = build_menu_buttons(["Play Defender", "Play Attacker"], start_y=465)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if state == "menu" and event.type == pygame.MOUSEBUTTONDOWN:
                for label, rect in difficulty_buttons.items():
                    if rect.collidepoint(event.pos):
                        if label == "Easy":
                            ai_depth = 1
                        elif label == "Medium":
                            ai_depth = 3
                        else:
                            ai_depth = 5
                        selected_difficulty = label
                        break

                for label, rect in side_buttons.items():
                    if rect.collidepoint(event.pos):
                        human_side = "defender" if label == "Play Defender" else "attacker"
                        selected_side = label
                        break

                if start_button.collidepoint(event.pos) and selected_difficulty and selected_side:
                    controller.start_game()
                    state = "playing"
                    selected = None
                    valid_moves = []
                    if controller.current_turn != human_side:
                        controller.start_ai_move(ai_depth)

            if state == "playing" and event.type == pygame.MOUSEBUTTONDOWN:
                if controller.ai_thinking or controller.status != "ongoing":
                    continue
                cell = pos_to_cell(event.pos)
                if cell is None:
                    continue
                row, col = cell
                piece = controller.board[row][col]

                if controller.current_turn != human_side:
                    continue

                if selected and (row, col) in valid_moves:
                    sr, sc = selected
                    controller.make_move(sr, sc, row, col)
                    selected = None
                    valid_moves = []
                    if controller.status == "ongoing" and controller.current_turn != human_side:
                        controller.start_ai_move(ai_depth)
                elif human_side == "defender" and piece in ("d", "k"):
                    selected = (row, col)
                    valid_moves = controller.get_valid_moves(row, col)
                elif human_side == "attacker" and piece == "a":
                    selected = (row, col)
                    valid_moves = controller.get_valid_moves(row, col)
                else:
                    selected = None
                    valid_moves = []

            if state == "gameover" and event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    state = "menu"
                    selected_difficulty = None
                    selected_side = None

        if state == "playing" and controller.status != "ongoing":
            state = "gameover"

        renderer.draw_background(screen)

        if state == "menu":
            renderer.draw_combined_menu(
                screen,
                "Hnefatafl",
                "Select difficulty and side",
                [
                    {
                        "heading": "Difficulty",
                        "heading_y": 165,
                        "buttons": difficulty_buttons,
                        "selected": selected_difficulty,
                    },
                    {
                        "heading": "Side",
                        "heading_y": 430,
                        "buttons": side_buttons,
                        "selected": selected_side,
                    },
                ],
                start_button,
                bool(selected_difficulty and selected_side),
            )
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
