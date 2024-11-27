import pygame
import sys
import random
import os
from collections import deque
from button import Button

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

pygame.init()

# Game colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)

# Assests 
BG = pygame.image.load(resource_path("assets/Background.png"))
def get_font(size):
    return pygame.font.Font(resource_path("assets/font.ttf"), size)

# Game Variables
WIDTH, HEIGHT = 1280, 720
ROWS, COLS = 21, 36  
TILE_SIZE = min(WIDTH // (COLS + 2), HEIGHT // (ROWS + 2))  
MARGIN_X = (WIDTH - (COLS * TILE_SIZE)) // 2
MARGIN_Y = (HEIGHT - (ROWS * TILE_SIZE)) // 2
directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
player_pos = [1, 1]
exit_pos = [ROWS - 2, COLS - 2]
clock = pygame.time.Clock()
vision_radius = 20

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
wall_texture = pygame.image.load(resource_path("assets/wall.png"))
wall_texture = pygame.transform.scale(wall_texture, (TILE_SIZE, TILE_SIZE))

player_texture_right = pygame.image.load(resource_path("assets/player_right.png"))
player_texture_right = pygame.transform.scale(player_texture_right, (TILE_SIZE, TILE_SIZE))

player_texture_left = pygame.image.load(resource_path("assets/player_left.png"))
player_texture_left = pygame.transform.scale(player_texture_left, (TILE_SIZE, TILE_SIZE))

exit_texture = pygame.image.load(resource_path("assets/exit.png"))
exit_texture = pygame.transform.scale(exit_texture, (TILE_SIZE, TILE_SIZE))

# Variable to track player direction
player_direction = "right"

# Drawing Functions
def draw_maze(ai_footprints, first_move):
    for row in range(ROWS):
        for col in range(COLS):
            x, y = MARGIN_X + col * TILE_SIZE, MARGIN_Y + row * TILE_SIZE
            
            # Calculate the distance between the player and the current tile
            distance = ((player_pos[0] - row) ** 2 + (player_pos[1] - col) ** 2) ** 0.5
            
            # Fog of War: Show fog for tiles outside the vision radius, only after the first move
            if first_move and distance > vision_radius:
                pygame.draw.rect(SCREEN, GRAY, (x, y, TILE_SIZE, TILE_SIZE))
            else:
                if maze[row][col] == 1:  # Wall
                    SCREEN.blit(wall_texture, (x, y))
                else:  # Path
                    pygame.draw.rect(SCREEN, "#1b1b1b", (x, y, TILE_SIZE, TILE_SIZE))
    
    # AI footprints
    for footprint in ai_footprints:
        fx, fy = footprint[1], footprint[0]
        pygame.draw.rect(SCREEN, YELLOW, (MARGIN_X + fx * TILE_SIZE, MARGIN_Y + fy * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    
    # Draw Player
    px, py = player_pos[1], player_pos[0]
    if player_direction == "right":
        SCREEN.blit(player_texture_right, (MARGIN_X + px * TILE_SIZE, MARGIN_Y + py * TILE_SIZE))
    else:
        SCREEN.blit(player_texture_left, (MARGIN_X + px * TILE_SIZE, MARGIN_Y + py * TILE_SIZE))
    
    # Draw Exit
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

# Paue menu
def pause_menu():
    while True:
        SCREEN.blit(BG, (0, 0))
        PAUSE_MOUSE_POS = pygame.mouse.get_pos()

        # Pause Menu Text
        PAUSE_TEXT = get_font(30).render("Game Paused", True, "Red")
        PAUSE_RECT = PAUSE_TEXT.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        SCREEN.blit(PAUSE_TEXT, PAUSE_RECT)

        # Pause Menu Buttons
        CONTINUE_BUTTON = Button(image=None, pos=(WIDTH // 2, HEIGHT // 2), text_input="CONTINUE", font=get_font(40), base_color="White", hovering_color="Red")
        EXIT_BUTTON = Button(image=None, pos=(WIDTH // 2, HEIGHT // 2 + 100), text_input="EXIT", font=get_font(40), base_color="White", hovering_color="Red")

        for button in [CONTINUE_BUTTON, EXIT_BUTTON]:
            button.changeColor(PAUSE_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if CONTINUE_BUTTON.checkForInput(PAUSE_MOUSE_POS):
                    return  # Resume game
                if EXIT_BUTTON.checkForInput(PAUSE_MOUSE_POS):
                    main_menu()  # Go back to main menu

        pygame.display.update()

# Game main function
def game_main():
    global player_pos, maze, player_direction, vision_radius
    maze = generate_complex_maze()
    player_pos = [1, 1]
    ai_mode = False
    solution_path = []
    ai_footprints = []
    first_move = False  # Flag to track if the first move has been made

    while True:
        SCREEN.fill(BLACK)

        # Draw the maze with or without fog depending on the first move
        draw_maze(ai_footprints, first_move)

        if ai_mode and solution_path:
            if player_pos != exit_pos:
                ai_footprints.append(player_pos[:])
                player_pos[:] = solution_path.pop(0)

        # Check if vision_radius reached 0, end the game
        if vision_radius <= 0:
            game_over_text = get_font(75).render("Game Over!", True, RED)
            SCREEN.blit(game_over_text, game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            pygame.display.flip()
            pygame.time.delay(2000)  # Wait for 2 seconds
            main_menu()  # Return to the main menu after game over

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_menu()  # Open pause menu
                if event.key == pygame.K_m:
                    ai_mode = not ai_mode
                    if ai_mode:
                        solution_path = bfs_solve(player_pos, exit_pos)
                        if not solution_path:
                            print("No path found!")
                            ai_mode = False
                if not ai_mode:  # Manual mode
                    new_pos = player_pos[:]
                    moved = False  # Track if player moved

                    if event.key == pygame.K_UP:
                        new_pos[0] -= 1
                        moved = True
                    elif event.key == pygame.K_DOWN:
                        new_pos[0] += 1
                        moved = True
                    elif event.key == pygame.K_LEFT:
                        new_pos[1] -= 1
                        player_direction = "left"
                        moved = True
                    elif event.key == pygame.K_RIGHT:
                        new_pos[1] += 1
                        player_direction = "right"
                        moved = True

                    # Update player position if the new position is valid
                    if maze[new_pos[0]][new_pos[1]] == 0:
                        player_pos = new_pos
                        # Set first_move to True after the first movement
                        if not first_move:
                            first_move = True
                            vision_radius = 20  # Reset vision radius when the first move happens

                    # Reduce vision radius if the player moves
                    if moved:
                        vision_radius = max(0, vision_radius - 0.1)  # Prevent radius from going below 0

        if player_pos == exit_pos:
            TEXT = get_font(75).render("Level complete!", True, WHITE)
            SCREEN.blit(TEXT, TEXT.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            pygame.display.flip()
            pygame.time.delay(1000)
            main_menu()  # Return to main menu after completing the level

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

        PLAY_BUTTON = Button(image=pygame.image.load(resource_path("assets/Play Rect.png")), pos=(640, 250), text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="Red")
        HOW_TO_PLAY_BUTTON = Button(image=pygame.image.load(resource_path("assets/Options Rect.png")), pos=(640, 400), text_input="HOW TO PLAY", font=get_font(50), base_color="#d7fcd4", hovering_color="Red")
        QUIT_BUTTON = Button(image=pygame.image.load(resource_path("assets/Quit Rect.png")), pos=(640, 550), text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="Red")

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
                    reset_game()  # Reset game state before starting new game
                    play()
                if HOW_TO_PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    how_to_play()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

def reset_game():
    """Reset all necessary game variables for a fresh start."""
    global player_pos, maze, player_direction, vision_radius
    maze = generate_complex_maze()
    player_pos = [1, 1]
    player_direction = "right"
    vision_radius = 20  # Reset vision radius

main_menu()