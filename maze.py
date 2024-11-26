import pygame
import sys
import random
from collections import deque
from button import Button

pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Font and Background
BG = pygame.image.load("assets/Background.png")
def get_font(size):
    return pygame.font.Font("assets/font.ttf", size)

# Game Variables
WIDTH, HEIGHT = 1280, 720
ROWS, COLS = 21, 36  # Ensure an odd number for better maze generation
TILE_SIZE = min(WIDTH // (COLS + 2), HEIGHT // (ROWS + 2))  # Add margins
MARGIN_X = (WIDTH - (COLS * TILE_SIZE)) // 2
MARGIN_Y = (HEIGHT - (ROWS * TILE_SIZE)) // 2
directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
player_pos = [1, 1]
exit_pos = [ROWS - 2, COLS - 2]
clock = pygame.time.Clock()

# Screen Dimensions
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("THE MAZE")

# Maze Generation
def generate_complex_maze():
    maze = [[1 for _ in range(COLS)] for _ in range(ROWS)]

    def carve_path(x, y):
        maze[x][y] = 0
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + 2 * dx, y + 2 * dy
            if 1 <= nx < ROWS - 1 and 1 <= ny < COLS - 1 and maze[nx][ny] == 1:
                maze[x + dx][y + dy] = 0
                carve_path(nx, ny)

    carve_path(1, 1)
    maze[1][1] = 0
    maze[ROWS - 2][COLS - 2] = 0
    return maze

maze = generate_complex_maze()

# Load textures
wall_texture = pygame.image.load("assets/wall.png")
wall_texture = pygame.transform.scale(wall_texture, (TILE_SIZE, TILE_SIZE))

player_texture_right = pygame.image.load("assets/player_right.png")
player_texture_right = pygame.transform.scale(player_texture_right, (TILE_SIZE, TILE_SIZE))

player_texture_left = pygame.image.load("assets/player_left.png")
player_texture_left = pygame.transform.scale(player_texture_left, (TILE_SIZE, TILE_SIZE))

exit_texture = pygame.image.load("assets/exit.png")
exit_texture = pygame.transform.scale(exit_texture, (TILE_SIZE, TILE_SIZE))

# Variable to track player direction
player_direction = "right"

# Drawing Functions
def draw_maze(ai_footprints):
    for row in range(ROWS):
        for col in range(COLS):
            x, y = MARGIN_X + col * TILE_SIZE, MARGIN_Y + row * TILE_SIZE
            if maze[row][col] == 1: 
                SCREEN.blit(wall_texture, (x, y))
            else:  # Path
                pygame.draw.rect(SCREEN, "#1b1b1b", (x, y, TILE_SIZE, TILE_SIZE))
    for footprint in ai_footprints:
        fx, fy = footprint[1], footprint[0]
        pygame.draw.rect(SCREEN, YELLOW, (MARGIN_X + fx * TILE_SIZE, MARGIN_Y + fy * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # Draw player based on direction
    px, py = player_pos[1], player_pos[0]
    if player_direction == "right":
        SCREEN.blit(player_texture_right, (MARGIN_X + px * TILE_SIZE, MARGIN_Y + py * TILE_SIZE))
    else:
        SCREEN.blit(player_texture_left, (MARGIN_X + px * TILE_SIZE, MARGIN_Y + py * TILE_SIZE))

    # Draw exit
    ex, ey = exit_pos[1], exit_pos[0]
    SCREEN.blit(exit_texture, (MARGIN_X + ex * TILE_SIZE, MARGIN_Y + ey * TILE_SIZE))


def bfs_solve(start, end):
    queue = deque([start])
    visited = set()
    visited.add(tuple(start))
    parent = {tuple(start): None}

    while queue:
        current = queue.popleft()
        if current == end:
            path = []
            while current:
                path.append(current)
                current = parent[tuple(current)]
            return path[::-1]
        for dx, dy in directions:
            next_row, next_col = current[0] + dx, current[1] + dy
            if 1 <= next_row < ROWS - 1 and 1 <= next_col < COLS - 1 and maze[next_row][next_col] == 0:
                next_pos = [next_row, next_col]
                if tuple(next_pos) not in visited:
                    visited.add(tuple(next_pos))
                    parent[tuple(next_pos)] = current
                    queue.append(next_pos)
    return []

# Game Logic
def game_main():
    global player_pos, maze, player_direction
    maze = generate_complex_maze()
    player_pos = [1, 1]
    ai_mode = False
    solution_path = []
    ai_footprints = []

    while True:
        SCREEN.fill(BLACK)
        draw_maze(ai_footprints)

        if ai_mode and solution_path:
            if player_pos != exit_pos:
                ai_footprints.append(player_pos[:])
                player_pos[:] = solution_path.pop(0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    ai_mode = not ai_mode
                    if ai_mode:
                        solution_path = bfs_solve(player_pos, exit_pos)
                        if not solution_path:
                            print("No path found!")
                            ai_mode = False
                if not ai_mode:
                    new_pos = player_pos[:]
                    if event.key == pygame.K_UP:
                        new_pos[0] -= 1
                    elif event.key == pygame.K_DOWN:
                        new_pos[0] += 1
                    elif event.key == pygame.K_LEFT:
                        new_pos[1] -= 1
                        player_direction = "left"  # Update direction
                    elif event.key == pygame.K_RIGHT:
                        new_pos[1] += 1
                        player_direction = "right"  # Update direction
                    if maze[new_pos[0]][new_pos[1]] == 0:
                        player_pos = new_pos

        if player_pos == exit_pos:
            TEXT = get_font(50).render("Level complete!", True, RED)
            SCREEN.blit(TEXT, TEXT.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            pygame.display.flip()
            pygame.time.delay(2000)
            return

        pygame.display.flip()
        clock.tick(30)

# Menu Functions
def play():
    game_main()

def how_to_play():
    while True:
        HOW_TOP_PLAY_POS = pygame.mouse.get_pos()

        SCREEN.blit(BG, (0, 0))

        TEXT = get_font(30).render("HOW TO PLAY", True, "Red")
        TEXT_RECT = TEXT.get_rect(center=(640, 50))
        SCREEN.blit(TEXT, TEXT_RECT)

        HTP_TEXT = get_font(15).render("Use arrow keys to move the player in Manual Mode", True, "White")
        HTEXT_RECT = HTP_TEXT.get_rect(center=(640, 250))
        SCREEN.blit(HTP_TEXT, HTEXT_RECT)

        AI_TEXT = get_font(15).render("Press M to toggle AI Mode, where the AI solves the maze automatically.", True, "White")
        AI_RECT = AI_TEXT.get_rect(center=(640, 350))
        SCREEN.blit(AI_TEXT, AI_RECT)

        BACK = Button(image=None, pos=(640, 660), 
                            text_input="BACK", font=get_font(20), base_color="White", hovering_color="Red")

        BACK.changeColor(HOW_TOP_PLAY_POS)
        BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK.checkForInput(HOW_TOP_PLAY_POS):
                    main_menu()

        pygame.display.update()

def main_menu():
    while True:
        SCREEN.blit(BG, (0, 0))
        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("THE MAZE", True, "RED")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(640, 250), text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="Red")
        HOW_TO_PLAY_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(640, 400), text_input="HOW TO PLAY", font=get_font(50), base_color="#d7fcd4", hovering_color="Red")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 550), text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="Red")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, HOW_TO_PLAY_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if HOW_TO_PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    how_to_play()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu()
