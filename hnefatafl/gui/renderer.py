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
    COLOR_PANEL_DARK,
    COLOR_PANEL_LINE,
    COLOR_SELECT,
    COLOR_TEXT,
    COLOR_THRONE,
    COLOR_VALID,
    FONT_TITLE,
    FONT_UI,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    PANEL_HEIGHT,
    SIDEBAR_ORIGIN,
    SIDEBAR_WIDTH,
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

    def draw_board(self, screen, board, selected, valid_moves, anim=None):
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
        skip_positions = set()
        if anim:
            skip_positions.add(anim["from"])
            skip_positions.add(anim["to"])
            for cap in anim["captures"]:
                skip_positions.add((cap[0], cap[1]))

        for r, row in enumerate(board):
            for c, cell in enumerate(row):
                if cell == "e" or (r, c) in skip_positions:
                    continue
                center = (
                    origin_x + c * CELL_SIZE + CELL_SIZE // 2,
                    origin_y + r * CELL_SIZE + CELL_SIZE // 2,
                )
                self._draw_piece(screen, cell, center)

        if anim:
            self._draw_animation(screen, anim)

    def draw_moves_panel(
        self,
        screen,
        move_rows,
        scroll_offset,
        up_button,
        down_button,
        prev_button,
        next_button,
        replay_active,
        restart_button,
    ):
        panel_x, panel_y = SIDEBAR_ORIGIN
        panel_h = SCREEN_HEIGHT - PANEL_HEIGHT - panel_y
        panel_rect = pygame.Rect(panel_x, panel_y, SIDEBAR_WIDTH, panel_h)
        pygame.draw.rect(screen, COLOR_PANEL_DARK, panel_rect, border_radius=12)

        title = self.ui_font.render("Moves", True, COLOR_TEXT)
        screen.blit(title, (panel_x + 16, panel_y + 12))

        header_y = panel_y + 40
        pygame.draw.line(screen, COLOR_PANEL_LINE, (panel_x + 12, header_y), (panel_x + SIDEBAR_WIDTH - 12, header_y), 1)

        list_top = header_y + 12
        row_h = 24
        visible_rows = int((panel_h - 120) // row_h)
        start = max(0, min(scroll_offset, max(0, len(move_rows) - visible_rows)))

        for idx in range(start, min(len(move_rows), start + visible_rows)):
            row = move_rows[idx]
            y = list_top + (idx - start) * row_h
            if row.get("highlight"):
                highlight = pygame.Rect(panel_x + 12, y - 2, SIDEBAR_WIDTH - 24, row_h)
                pygame.draw.rect(screen, COLOR_SELECT, highlight, 0, border_radius=6)
            left = self.small_font.render(row["left"], True, COLOR_TEXT)
            right = self.small_font.render(row["right"], True, COLOR_TEXT)
            screen.blit(left, (panel_x + 18, y))
            screen.blit(right, (panel_x + SIDEBAR_WIDTH // 2 + 6, y))

        for btn, label in [(up_button, "^"), (down_button, "v")]:
            pygame.draw.rect(screen, COLOR_PANEL, btn, border_radius=6)
            text = self.small_font.render(label, True, COLOR_TEXT)
            screen.blit(text, (btn.centerx - text.get_width() // 2, btn.centery - text.get_height() // 2))

        if replay_active:
            for btn, label in [(prev_button, "<"), (next_button, ">")]:
                pygame.draw.rect(screen, COLOR_PANEL, btn, border_radius=8)
                text = self.small_font.render(label, True, COLOR_TEXT)
                screen.blit(text, (btn.centerx - text.get_width() // 2, btn.centery - text.get_height() // 2))

            pygame.draw.rect(screen, COLOR_PANEL, restart_button, border_radius=8)
            label = self.small_font.render("Restart", True, COLOR_TEXT)
            screen.blit(
                label,
                (restart_button.centerx - label.get_width() // 2, restart_button.centery - label.get_height() // 2),
            )

    def _draw_piece(self, screen, cell, center, alpha=255):
        radius = CELL_SIZE // 2 - 6
        if cell == "k":
            radius = CELL_SIZE // 2 - 5

        if alpha >= 255:
            if cell == "a":
                pygame.draw.circle(screen, COLOR_ATTACKER, center, radius)
            elif cell == "d":
                pygame.draw.circle(screen, COLOR_DEFENDER, center, radius)
                pygame.draw.circle(screen, COLOR_GRID, center, radius, 2)
            elif cell == "k":
                pygame.draw.circle(screen, COLOR_KING, center, radius)
                king = self.ui_font.render("♔", True, COLOR_TEXT)
                screen.blit(
                    king,
                    (center[0] - king.get_width() // 2, center[1] - king.get_height() // 2),
                )
            return

        size = radius * 2 + 4
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        local_center = (size // 2, size // 2)
        if cell == "a":
            pygame.draw.circle(surface, (*COLOR_ATTACKER, alpha), local_center, radius)
        elif cell == "d":
            pygame.draw.circle(surface, (*COLOR_DEFENDER, alpha), local_center, radius)
            pygame.draw.circle(surface, (*COLOR_GRID, alpha), local_center, radius, 2)
        elif cell == "k":
            pygame.draw.circle(surface, (*COLOR_KING, alpha), local_center, radius)
            king = self.ui_font.render("♔", True, COLOR_TEXT)
            king.set_alpha(alpha)
            surface.blit(
                king,
                (local_center[0] - king.get_width() // 2, local_center[1] - king.get_height() // 2),
            )
        screen.blit(surface, (center[0] - size // 2, center[1] - size // 2))

    def _draw_animation(self, screen, anim):
        origin_x, origin_y = BOARD_ORIGIN
        move_t = anim["move_t"]
        cap_t = anim["cap_t"]
        (r1, c1) = anim["from"]
        (r2, c2) = anim["to"]
        start_x = origin_x + c1 * CELL_SIZE + CELL_SIZE // 2
        start_y = origin_y + r1 * CELL_SIZE + CELL_SIZE // 2
        end_x = origin_x + c2 * CELL_SIZE + CELL_SIZE // 2
        end_y = origin_y + r2 * CELL_SIZE + CELL_SIZE // 2
        cur_x = int(start_x + (end_x - start_x) * move_t)
        cur_y = int(start_y + (end_y - start_y) * move_t)

        self._draw_piece(screen, anim["piece"], (cur_x, cur_y))

        fade_alpha = int(255 * (1.0 - cap_t))
        for cap_r, cap_c, cap_piece in anim["captures"]:
            center = (
                origin_x + cap_c * CELL_SIZE + CELL_SIZE // 2,
                origin_y + cap_r * CELL_SIZE + CELL_SIZE // 2,
            )
            self._draw_piece(screen, cap_piece, center, fade_alpha)

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

    def draw_game_over(self, screen, winner, board_rect, overlay_alpha):
        if overlay_alpha > 0:
            overlay = pygame.Surface((board_rect.width, board_rect.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, overlay_alpha))
            screen.blit(overlay, (board_rect.x, board_rect.y))

        text = self.ui_font.render(f"{winner} wins", True, (0, 0, 0))
        x = board_rect.centerx - text.get_width() // 2
        y = board_rect.y - text.get_height() - 8
        screen.blit(text, (x, y))
