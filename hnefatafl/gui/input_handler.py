from ..constants import BOARD_ORIGIN, BOARD_PIXELS, CELL_SIZE


def pos_to_cell(pos):
    x, y = pos
    origin_x, origin_y = BOARD_ORIGIN
    if x < origin_x or y < origin_y:
        return None
    if x >= origin_x + BOARD_PIXELS or y >= origin_y + BOARD_PIXELS:
        return None
    col = (x - origin_x) // CELL_SIZE
    row = (y - origin_y) // CELL_SIZE
    return int(row), int(col)
