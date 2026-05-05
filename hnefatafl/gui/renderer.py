import pygame

from ..constants import (
    BOARD_ORIGIN,
    BOARD_SIZE,
    CELL_SIZE,
    COLOR_ATTACKER,
    COLOR_BG_BOTTOM,
    COLOR_BG_TOP,
    COLOR_BOARD,
    COLOR_CORNER,
    COLOR_DEFENDER,
    COLOR_GRID,
    COLOR_KING,
    COLOR_PANEL,
    COLOR_SELECT,
    COLOR_TEXT,
    COLOR_THRONE,
    COLOR_VALID,
    FONT_TITLE,
    FONT_UI,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    PANEL_HEIGHT,
)


class Renderer:
    def __init__(self):
        pygame.font.init()
        self.title_font = pygame.font.SysFont(FONT_TITLE, 48)
        self.ui_font = pygame.font.SysFont(FONT_UI, 22)
        self.small_font = pygame.font.SysFont(FONT_UI, 18)

    def draw_background(self, screen):
        # Subtle vertical gradient for atmosphere
        for y in range(SCREEN_HEIGHT):
            blend = y / float(SCREEN_HEIGHT)
            r = int(COLOR_BG_TOP[0] * (1 - blend) + COLOR_BG_BOTTOM[0] * blend)
            g = int(COLOR_BG_TOP[1] * (1 - blend) + COLOR_BG_BOTTOM[1] * blend)
            b = int(COLOR_BG_TOP[2] * (1 - blend) + COLOR_BG_BOTTOM[2] * blend)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    def draw_menu_screen(self, screen, title_text, subtitle_text, buttons):
        self.draw_background(screen)
        title = self.title_font.render(title_text, True, COLOR_TEXT)
        subtitle = self.ui_font.render(subtitle_text, True, COLOR_TEXT)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 90))
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 150))

        for label, rect in buttons.items():
            pygame.draw.rect(screen, COLOR_PANEL, rect, border_radius=8)
            text = self.ui_font.render(label, True, COLOR_TEXT)
            screen.blit(
                text,
                (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2),
            )

    def draw_combined_menu(self, screen, title_text, subtitle_text, groups, start_button, start_enabled):
        self.draw_background(screen)
        title = self.title_font.render(title_text, True, COLOR_TEXT)
        subtitle = self.ui_font.render(subtitle_text, True, COLOR_TEXT)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 125))

        for group in groups:
            heading = self.ui_font.render(group["heading"], True, COLOR_TEXT)
            screen.blit(heading, (SCREEN_WIDTH // 2 - heading.get_width() // 2, group["heading_y"]))

            for label, rect in group["buttons"].items():
                pygame.draw.rect(screen, COLOR_PANEL, rect, border_radius=8)
                if group.get("selected") == label:
                    pygame.draw.rect(screen, COLOR_SELECT, rect, 3, border_radius=8)
                text = self.ui_font.render(label, True, COLOR_TEXT)
                screen.blit(
                    text,
                    (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2),
                )

        pygame.draw.rect(screen, COLOR_PANEL, start_button, border_radius=10)
        if start_enabled:
            pygame.draw.rect(screen, COLOR_SELECT, start_button, 3, border_radius=10)
        label = self.ui_font.render("Start", True, COLOR_TEXT)
        screen.blit(
            label,
            (start_button.centerx - label.get_width() // 2, start_button.centery - label.get_height() // 2),
        )

    def draw_board(self, screen, board, selected, valid_moves):
        origin_x, origin_y = BOARD_ORIGIN
        board_rect = pygame.Rect(origin_x, origin_y, BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE)
        pygame.draw.rect(screen, COLOR_BOARD, board_rect)

        # Special squares
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                cell_rect = pygame.Rect(
                    origin_x + c * CELL_SIZE,
                    origin_y + r * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                )
                if (r, c) in [(0, 0), (0, 10), (10, 0), (10, 10)]:
                    pygame.draw.rect(screen, COLOR_CORNER, cell_rect)
                if (r, c) == (5, 5):
                    pygame.draw.rect(screen, COLOR_THRONE, cell_rect)

        # Grid
        for i in range(BOARD_SIZE + 1):
            x = origin_x + i * CELL_SIZE
            y = origin_y + i * CELL_SIZE
            pygame.draw.line(screen, COLOR_GRID, (x, origin_y), (x, origin_y + BOARD_SIZE * CELL_SIZE), 2)
            pygame.draw.line(screen, COLOR_GRID, (origin_x, y), (origin_x + BOARD_SIZE * CELL_SIZE, y), 2)

        # Highlights
        if selected:
            sr, sc = selected
            sel_rect = pygame.Rect(
                origin_x + sc * CELL_SIZE,
                origin_y + sr * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            pygame.draw.rect(screen, COLOR_SELECT, sel_rect, 4)

        for (r, c) in valid_moves:
            center = (
                origin_x + c * CELL_SIZE + CELL_SIZE // 2,
                origin_y + r * CELL_SIZE + CELL_SIZE // 2,
            )
            pygame.draw.circle(screen, COLOR_VALID, center, CELL_SIZE // 6)

        # Pieces
        for r, row in enumerate(board):
            for c, cell in enumerate(row):
                if cell == "e":
                    continue
                center = (
                    origin_x + c * CELL_SIZE + CELL_SIZE // 2,
                    origin_y + r * CELL_SIZE + CELL_SIZE // 2,
                )
                if cell == "a":
                    pygame.draw.circle(screen, COLOR_ATTACKER, center, CELL_SIZE // 2 - 6)
                elif cell == "d":
                    pygame.draw.circle(screen, COLOR_DEFENDER, center, CELL_SIZE // 2 - 6)
                    pygame.draw.circle(screen, COLOR_GRID, center, CELL_SIZE // 2 - 6, 2)
                elif cell == "k":
                    pygame.draw.circle(screen, COLOR_KING, center, CELL_SIZE // 2 - 5)
                    king = self.ui_font.render("♔", True, COLOR_TEXT)
                    screen.blit(
                        king,
                        (center[0] - king.get_width() // 2, center[1] - king.get_height() // 2),
                    )

    def draw_status(self, screen, turn, captured_attackers, captured_defenders):
        panel_rect = pygame.Rect(0, SCREEN_HEIGHT - PANEL_HEIGHT, SCREEN_WIDTH, PANEL_HEIGHT)
        pygame.draw.rect(screen, COLOR_PANEL, panel_rect)
        turn_text = self.ui_font.render(f"Turn: {turn}", True, COLOR_TEXT)
        cap_text = self.small_font.render(
            f"Captured A: {captured_attackers}  |  Captured D: {captured_defenders}",
            True,
            COLOR_TEXT,
        )
        screen.blit(turn_text, (30, SCREEN_HEIGHT - PANEL_HEIGHT + 18))
        screen.blit(cap_text, (30, SCREEN_HEIGHT - PANEL_HEIGHT + 50))

    def draw_thinking_overlay(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 90))
        screen.blit(overlay, (0, 0))
        text = self.title_font.render("Thinking...", True, (255, 245, 230))
        screen.blit(
            text,
            (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2),
        )

    def draw_game_over(self, screen, winner, button_rect):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 110))
        screen.blit(overlay, (0, 0))

        text = self.title_font.render(f"{winner} wins", True, (255, 245, 230))
        screen.blit(
            text,
            (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 120),
        )

        pygame.draw.rect(screen, COLOR_PANEL, button_rect, border_radius=10)
        label = self.ui_font.render("Restart", True, COLOR_TEXT)
        screen.blit(
            label,
            (button_rect.centerx - label.get_width() // 2, button_rect.centery - label.get_height() // 2),
        )
