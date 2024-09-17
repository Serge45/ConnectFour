import sys
import time
import pygame
import pygame.freetype

pygame.init()
screen = pygame.display.set_mode(
    (
        1024,
        768,
    ),
    pygame.SRCALPHA,
    32,
)
pygame.display.set_caption("Connect Four")

NUM_BOARD_ROWS = 6
NUM_BOARD_COLS = 7
BOARD_COLOR = (
    100,
    100,
    255,
    255,
)
GRID_COLOR = (
    0,
    0,
    0,
    255,
)
EMPTY_COLOR = (
    0,
    0,
    0,
    255,
)
HIGHLIGHTED_COL_COLOR = (255, 0, 0, 10)
PLAYER_COLORS = [
    (
        255,
        0,
        0,
    ),
    (255, 255, 0),
]
FPS = 60

highlighted_col = 0
board_status = [[None] * NUM_BOARD_ROWS for _ in range(NUM_BOARD_COLS)]
current_player = 0
players = [0, 1]


def draw_board(surface: pygame.Surface):
    w, h = surface.get_width(), surface.get_height()
    pygame.draw.rect(
        surface,
        BOARD_COLOR,
        (
            0,
            0,
            w,
            h,
        ),
    )
    grid_x, grid_y = w // NUM_BOARD_COLS, h // NUM_BOARD_ROWS

    for x in range(0, w, grid_x):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, h))

    for y in range(0, h, grid_y):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (w, y))

    for x in range(0, w, grid_x):
        for y in range(0, h, grid_y):
            col = min(x // grid_x, NUM_BOARD_COLS - 1)
            row = min(y // grid_y, NUM_BOARD_ROWS - 1)
            player = board_status[col][row]
            color = EMPTY_COLOR if player is None else PLAYER_COLORS[player]
            pygame.draw.ellipse(
                surface,
                color,
                (x + grid_x * 0.05, y + 0.05 * grid_y, grid_x * 0.9, grid_y * 0.9),
            )

    if highlighted_col is not None:
        pygame.draw.rect(
            surface,
            PLAYER_COLORS[current_player],
            (highlighted_col * grid_x, 0, grid_x, h),
            width=2,
        )
        for i, row in enumerate(reversed(board_status[highlighted_col])):
            if row is None:
                x = grid_x * highlighted_col
                y = grid_y * (NUM_BOARD_ROWS - i - 1)
                pygame.draw.ellipse(
                    surface,
                    PLAYER_COLORS[current_player],
                    (x + grid_x * 0.05, y + 0.05 * grid_y, grid_x * 0.9, grid_y * 0.9),
                    4,
                )
                break


def fill_background():
    screen.fill((0, 0, 0, 255))


def update_highlighed_col(evt, surface: pygame.Surface):
    x, _ = pygame.mouse.get_pos()
    x -= (screen.get_rect().width - surface.get_rect().width) // 2
    grid_x = surface.get_width() // NUM_BOARD_COLS
    global highlighted_col
    highlighted_col = min(x // grid_x, NUM_BOARD_COLS - 1)


def on_mouse_clicked(evt):
    global board_status
    global current_player
    global players
    col = board_status[highlighted_col]

    for i in reversed(range(len(col))):
        if col[i] is None:
            col[i] = players[current_player]
            current_player = (current_player + 1) % 2
            break


def check_winner():
    def check(col):
        if len(col) < 4:
            return None

        for i in range(len(col) - 4 + 1):
            p = set(col[i : i + 4])

            if None not in p and len(p) == 1:
                return p.pop()

    lines = []

    for dir in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
        for c in range(NUM_BOARD_COLS):
            for r in range(NUM_BOARD_ROWS):
                line = []
                bound = max(NUM_BOARD_COLS, NUM_BOARD_ROWS)

                for offset in range(bound):
                    x = c + offset * dir[0]
                    y = r + offset * dir[1]

                    if x < NUM_BOARD_COLS and y < NUM_BOARD_ROWS and x >= 0 and y >= 0:
                        line.append(board_status[x][y])
                    else:
                        break

                lines.append(line)

    for r in range(NUM_BOARD_ROWS):
        lines.append([c[r] for c in board_status])

    for line in board_status + lines:
        winner = check(line)
        if winner is not None:
            return winner


def draw_winner(winner, surface: pygame.Surface):
    pygame.draw.rect(surface, (50, 50, 50), surface.get_rect())
    font: pygame.freetype.Font = pygame.freetype.SysFont(None, 40)
    s, r = font.render("Win", PLAYER_COLORS[winner])
    r = r.move(
        surface.get_rect().centerx - r.centerx, surface.get_rect().centery - r.centery
    )
    surface.blit(s, r)


def reset_board():
    global board_status
    global current_player
    board_status = [[None] * NUM_BOARD_ROWS for _ in range(NUM_BOARD_COLS)]
    current_player = 0


def flip():
    PLAYER_COLORS[0], PLAYER_COLORS[1] = PLAYER_COLORS[1], PLAYER_COLORS[0]


board_surface = pygame.Surface((int(1024 * 0.9), int(768 * 0.9)), pygame.SRCALPHA, 32)
winner_surface = pygame.Surface((200, 100), pygame.SRCALPHA, 32)

fill_background()
clock = pygame.time.Clock()

while True:
    for evt in pygame.event.get():
        if evt.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif evt.type == pygame.KEYDOWN and evt.key == pygame.K_r:
            reset_board()
        elif (winner := check_winner()) is not None:
            draw_winner(winner, winner_surface)
        elif evt.type == pygame.KEYDOWN and evt.key == pygame.K_F1:
            flip()
        elif evt.type == pygame.MOUSEMOTION:
            update_highlighed_col(evt, board_surface)
        elif evt.type == pygame.MOUSEBUTTONUP:
            on_mouse_clicked(evt)

    draw_board(board_surface)
    screen.blit(
        board_surface,
        (
            (screen.get_width() - board_surface.get_width()) // 2,
            (screen.get_height() - board_surface.get_height()) // 2,
        ),
    )

    if winner is not None:
        x, y = screen.get_rect().center
        x -= winner_surface.get_width() // 2
        y -= winner_surface.get_height() // 2
        screen.blit(
            winner_surface,
            (x, y, winner_surface.get_width(), winner_surface.get_height()),
        )

    pygame.display.update()
    clock.tick(FPS)
