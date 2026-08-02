"""
Classic Snake Game — Nokia 3310 style
--------------------------------------
Controls:
  Arrow Keys / WASD : move
  P                  : pause / unpause
  R                  : restart after game over
  ESC / close window : quit

Requirements:
  pip install pygame
"""
import pygame
import random
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CELL_SIZE = 20          # size of one grid cell in pixels
GRID_WIDTH = 30         # number of cells horizontally (inside the border)
GRID_HEIGHT = 20        # number of cells vertically (inside the border)
BORDER_THICKNESS = 20   # thickness of the outer wall, in pixels

SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE + BORDER_THICKNESS * 2
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE + BORDER_THICKNESS * 2 + 40  # +40 for score bar

FPS_RENDER = 60         # render FPS (independent of snake movement)
FPS_START = 8           # starting speed (snake moves per second)
FPS_MAX = 18            # speed cap so it doesn't get absurd
SPEEDUP_EVERY = 5       # every N apples, speed increases by 1

# --- Retro Nokia LCD colour palette -----------------------------------------
BG_COLOR = (30, 46, 30)          # dark olive-green "screen off" background
SCREEN_COLOR = (170, 200, 150)   # pale green LCD background
GRID_LINE_COLOR = (155, 188, 135)
SNAKE_COLOR = (30, 46, 30)       # dark pixels, like an old monochrome LCD
APPLE_COLOR = (30, 46, 30)
BORDER_COLOR = (20, 30, 20)
TEXT_COLOR = (30, 46, 30)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class SnakeGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake — Nokia Style")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        # Try a common monospace; pygame will fallback if not found
        self.font_small = pygame.font.SysFont("Courier New", 20, bold=True)
        self.font_big = pygame.font.SysFont("Courier New", 36, bold=True)

        # Custom event for snake movement (decoupled from rendering)
        self.MOVE_EVENT = pygame.USEREVENT + 1

        self.reset()

    def reset(self):
        cx, cy = GRID_WIDTH // 2, GRID_HEIGHT // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = RIGHT
        self.pending_direction = RIGHT
        self.apple = None
        self.score = 0
        self.speed = FPS_START
        self.game_over = False
        self.paused = False

        # spawn apple after snake is set up
        self.apple = self.spawn_apple()

        # (re)set movement timer according to speed
        self._set_move_timer()

    def _set_move_timer(self):
        # milliseconds per move (integer)
        ms = max(1, int(1000 / max(1, self.speed)))
        pygame.time.set_timer(self.MOVE_EVENT, ms)

    def spawn_apple(self):
        free_cells = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT) if (x, y) not in self.snake]
        if not free_cells:
            # no space left — player filled the board; treat as game over / win
            self.game_over = True
            return None
        return random.choice(free_cells)

    # -----------------------------------------------------------------
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset()
                    # ignore other keys when game over
                    continue

                if event.key == pygame.K_p:
                    # toggle paused state (do not change movement timer; just ignore MOVE_EVENT while paused)
                    self.paused = not self.paused
                    continue

                new_dir = None
                if event.key in (pygame.K_UP, pygame.K_w):
                    new_dir = UP
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    new_dir = DOWN
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    new_dir = LEFT
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    new_dir = RIGHT

                # Prevent the snake from reversing directly into itself.
                # Compare against pending_direction so multiple key presses within one frame cannot flip 180°.
                if new_dir is not None:
                    opposite_pending = (-self.pending_direction[0], -self.pending_direction[1])
                    if new_dir != opposite_pending:
                        self.pending_direction = new_dir

            # Movement is handled by MOVE_EVENT (see run loop)
            if event.type == self.MOVE_EVENT:
                # Only step if not paused and not game over
                if not self.paused and not self.game_over:
                    self._step()

    # -----------------------------------------------------------------
    def _step(self):
        # Apply pending direction
        self.direction = self.pending_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Wall collision -> game over (classic Nokia snake dies on walls)
        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            self.game_over = True
            return

        # Self collision
        if new_head in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if self.apple is not None and new_head == self.apple:
            self.score += 1
            self.apple = self.spawn_apple()
            # speed up every SPEEDUP_EVERY apples
            if self.score % SPEEDUP_EVERY == 0 and self.speed < FPS_MAX:
                self.speed += 1
                self._set_move_timer()
        else:
            self.snake.pop()  # move forward (remove tail) if no apple eaten

    # -----------------------------------------------------------------
    def draw(self):
        self.screen.fill(BG_COLOR)

        # Outer border ("wall")
        pygame.draw.rect(
            self.screen,
            BORDER_COLOR,
            (0, 40, SCREEN_WIDTH, SCREEN_HEIGHT - 40),
            border_radius=4,
        )

        # Inner LCD play area
        play_rect = pygame.Rect(
            BORDER_THICKNESS,
            40 + BORDER_THICKNESS,
            GRID_WIDTH * CELL_SIZE,
            GRID_HEIGHT * CELL_SIZE,
        )
        pygame.draw.rect(self.screen, SCREEN_COLOR, play_rect)

        # Faint grid lines for that pixelated LCD look
        for gx in range(GRID_WIDTH + 1):
            x = play_rect.left + gx * CELL_SIZE
            pygame.draw.line(self.screen, GRID_LINE_COLOR, (x, play_rect.top), (x, play_rect.bottom))
        for gy in range(GRID_HEIGHT + 1):
            y = play_rect.top + gy * CELL_SIZE
            pygame.draw.line(self.screen, GRID_LINE_COLOR, (play_rect.left, y), (play_rect.right, y))

        # Apple
        if self.apple is not None:
            self.draw_cell(self.apple, play_rect, APPLE_COLOR, shrink=3)

        # Snake
        for i, segment in enumerate(self.snake):
            shrink = 2 if i == 0 else 3  # head slightly bigger than body
            self.draw_cell(segment, play_rect, SNAKE_COLOR, shrink=shrink)

        # Score bar at the top
        score_surf = self.font_small.render(f"SCORE: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_surf, (10, 8))

        speed_surf = self.font_small.render(f"SPEED: {self.speed}", True, TEXT_COLOR)
        self.screen.blit(speed_surf, (SCREEN_WIDTH - speed_surf.get_width() - 10, 8))

        if self.paused and not self.game_over:
            self.draw_center_text("PAUSED", "Press P to resume")

        if self.game_over:
            self.draw_center_text("GAME OVER", f"Score: {self.score}  —  Press R to restart")

        pygame.display.flip()

    def draw_cell(self, cell, play_rect, color, shrink=2):
        gx, gy = cell
        rect = pygame.Rect(
            play_rect.left + gx * CELL_SIZE + shrink // 2,
            play_rect.top + gy * CELL_SIZE + shrink // 2,
            CELL_SIZE - shrink,
            CELL_SIZE - shrink,
        )
        pygame.draw.rect(self.screen, color, rect, border_radius=3)

    def draw_center_text(self, big_text, small_text):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 30, 20, 160))
        self.screen.blit(overlay, (0, 0))

        big_surf = self.font_big.render(big_text, True, SCREEN_COLOR)
        small_surf = self.font_small.render(small_text, True, SCREEN_COLOR)

        big_rect = big_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 15))
        small_rect = small_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25))

        self.screen.blit(big_surf, big_rect)
        self.screen.blit(small_surf, small_rect)

    # -----------------------------------------------------------------
    def run(self):
        # Ensure the MOVE_EVENT timer exists when starting
        self._set_move_timer()

        while True:
            self.handle_input()
            self.draw()
            # render at a steady 60 FPS
            self.clock.tick(FPS_RENDER)


if __name__ == "__main__":
    SnakeGame().run()