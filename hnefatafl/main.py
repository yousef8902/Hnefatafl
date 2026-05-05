import os
import sys
import time
from copy import deepcopy

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
    SIDEBAR_ORIGIN,
    SIDEBAR_WIDTH,
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


def build_move_rows(move_history, highlight_index):
    rows = []
    move_no = 1
    i = 0
    while i < len(move_history):
        left = move_history[i]["notation"] if i < len(move_history) else ""
        right = move_history[i + 1]["notation"] if i + 1 < len(move_history) else ""
        rows.append(
            {
                "left": f"{move_no}. {left}",
                "right": right,
                "highlight": highlight_index in (i, i + 1),
            }
        )
        move_no += 1
        i += 2
    return rows


def count_pieces(board):
    attackers = 0
    defenders = 0
    king = 0
    for row in board:
        for cell in row:
            if cell == "a":
                attackers += 1
            elif cell == "d":
                defenders += 1
            elif cell == "k":
                king += 1
    return attackers, defenders, king


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
    move_history = []
    board_history = []
    replay_index = None
    scroll_offset = 0
    anim_state = None
    pending_ai_move = False
    gameover_start = None
    restart_button = pygame.Rect(0, 0, 160, 36)
    start_button = pygame.Rect(
        SCREEN_WIDTH // 2 - 120,
        640,
        240,
        54,
    )

    difficulty_buttons = build_menu_buttons(["Easy", "Medium", "Hard"], start_y=200)
    side_buttons = build_menu_buttons(["Play Defender", "Play Attacker"], start_y=465)
    sidebar_x, sidebar_y = SIDEBAR_ORIGIN
    up_button = pygame.Rect(sidebar_x + SIDEBAR_WIDTH - 44, sidebar_y + 52, 28, 20)
    down_button = pygame.Rect(sidebar_x + SIDEBAR_WIDTH - 44, sidebar_y + 78, 28, 20)
    prev_button = pygame.Rect(sidebar_x + 20, SCREEN_HEIGHT - 70, 40, 28)
    next_button = pygame.Rect(sidebar_x + 70, SCREEN_HEIGHT - 70, 40, 28)
    restart_button = pygame.Rect(sidebar_x + SIDEBAR_WIDTH - 180, SCREEN_HEIGHT - 74, 160, 34)
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
                    move_history = []
                    board_history = [deepcopy(controller.board)]
                    replay_index = None
                    scroll_offset = 0
                    anim_state = None
                    state = "playing"
                    selected = None
                    valid_moves = []
                    if controller.current_turn != human_side:
                        controller.start_ai_move(ai_depth)
                        pending_ai_move = True

            if state == "playing" and event.type == pygame.MOUSEBUTTONDOWN:
                if controller.ai_thinking or controller.status != "ongoing" or anim_state is not None:
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
                    move_info = controller.make_move(sr, sc, row, col)
                    if move_info:
                        move_history.append(move_info)
                        board_history.append(deepcopy(controller.board))
                        anim_state = {
                            "start": time.time(),
                            "move_duration": 0.35,
                            "cap_duration": 1.0,
                            "info": move_info,
                        }
                    selected = None
                    valid_moves = []
                    if controller.status == "ongoing" and controller.current_turn != human_side:
                        controller.start_ai_move(ai_depth)
                        pending_ai_move = True
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
                    gameover_start = None

            if state in ("playing", "gameover") and event.type == pygame.MOUSEBUTTONDOWN:
                if up_button.collidepoint(event.pos):
                    scroll_offset = max(0, scroll_offset - 1)
                if down_button.collidepoint(event.pos):
                    scroll_offset += 1

            if state == "gameover" and event.type == pygame.MOUSEBUTTONDOWN:
                if prev_button.collidepoint(event.pos) and replay_index is not None:
                    replay_index = max(0, replay_index - 1)
                if next_button.collidepoint(event.pos) and replay_index is not None:
                    replay_index = min(len(board_history) - 1, replay_index + 1)

        if state == "playing" and controller.status != "ongoing":
            state = "gameover"
            replay_index = len(board_history) - 1
            selected = None
            valid_moves = []
            gameover_start = time.time()

        if pending_ai_move and not controller.ai_thinking:
            ai_info = controller.consume_last_move()
            pending_ai_move = False
            if ai_info:
                move_history.append(ai_info)
                board_history.append(deepcopy(controller.board))
                anim_state = {
                    "start": time.time(),
                    "move_duration": 0.35,
                    "cap_duration": 1.0,
                    "info": ai_info,
                }

        anim_payload = None
        if anim_state is not None:
            elapsed = time.time() - anim_state["start"]
            move_t = min(1.0, elapsed / anim_state["move_duration"])
            cap_elapsed = max(0.0, elapsed - anim_state["move_duration"])
            cap_t = min(1.0, cap_elapsed / anim_state["cap_duration"])
            info = anim_state["info"]
            anim_payload = {
                "from": info["from"],
                "to": info["to"],
                "piece": info["piece"],
                "captures": info["captures"],
                "move_t": move_t,
                "cap_t": cap_t,
            }
            if elapsed >= anim_state["move_duration"] + anim_state["cap_duration"]:
                anim_state = None

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
            if state == "gameover" and replay_index is not None:
                board_to_draw = board_history[replay_index]
            else:
                board_to_draw = controller.board

            renderer.draw_board(screen, board_to_draw, selected, valid_moves, anim_payload)
            attackers, defenders, _king = count_pieces(board_to_draw)
            captured_attackers = 24 - attackers
            captured_defenders = 12 - defenders
            renderer.draw_status(screen, controller.current_turn, captured_attackers, captured_defenders)

            highlight_index = None
            if state == "gameover" and replay_index is not None:
                highlight_index = replay_index - 1 if replay_index > 0 else None
            elif move_history:
                highlight_index = len(move_history) - 1

            move_rows = build_move_rows(move_history, highlight_index)
            max_scroll = max(0, len(move_rows) - 1)
            scroll_offset = max(0, min(scroll_offset, max_scroll))
            renderer.draw_moves_panel(
                screen,
                move_rows,
                scroll_offset,
                up_button,
                down_button,
                prev_button,
                next_button,
                state == "gameover",
                restart_button,
            )

            if controller.ai_thinking:
                renderer.draw_thinking_overlay(screen)

            if state == "gameover":
                winner = "Defender" if controller.status == "defender_wins" else "Attacker"
                human_won = (
                    (controller.status == "defender_wins" and human_side == "defender")
                    or (controller.status == "attacker_wins" and human_side == "attacker")
                )
                message_color = (30, 140, 60) if human_won else (170, 40, 40)
                board_rect = pygame.Rect(BOARD_ORIGIN[0], BOARD_ORIGIN[1], BOARD_PIXELS, BOARD_PIXELS)
                if gameover_start is None:
                    gameover_start = time.time()
                elapsed = time.time() - gameover_start
                fade_delay = 2.0
                fade_duration = 1.0
                if elapsed < fade_delay:
                    overlay_alpha = 110
                else:
                    fade_t = min(1.0, (elapsed - fade_delay) / fade_duration)
                    overlay_alpha = int(110 * (1.0 - fade_t))
                renderer.draw_game_over(screen, winner, board_rect, overlay_alpha, message_color)

        pygame.display.flip()
        clock.tick(60)

    controller.close()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
