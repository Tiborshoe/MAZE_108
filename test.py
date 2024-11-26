import pygame, sys

# Initialize Pygame
pygame.init()

# Screen size and setup
screen_w = 1280
screen_h = 720
screen = pygame.display.set_mode((screen_w, screen_h))
pygame.display.set_caption("Maze Solver")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (100, 100, 100)

# Maze
maze = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

tile_size = 60
player_position = [1, 1]
goal_position = [8, 5]
vision_radius = 5  # Initial vision radius

maze_width = len(maze[0]) * tile_size
maze_height = len(maze) * tile_size
maze_x_offset = (screen_w - maze_width) // 2
maze_y_offset = (screen_h - maze_height) // 2

def draw_maze():
    for y in range(len(maze)):
        for x in range(len(maze[y])):
            distance = ((player_position[0] - x) ** 2 + (player_position[1] - y) ** 2) ** 0.5
            color = WHITE if maze[y][x] == 0 else BLACK if distance <= vision_radius else GRAY
            pygame.draw.rect(screen, color, 
                             (maze_x_offset + x * tile_size, maze_y_offset + y * tile_size, tile_size, tile_size))

def draw_player():
    pygame.draw.rect(screen, GREEN, 
                     (maze_x_offset + player_position[0] * tile_size, maze_y_offset + player_position[1] * tile_size, tile_size, tile_size))

def draw_goal():
    pygame.draw.rect(screen, RED, 
                     (maze_x_offset + goal_position[0] * tile_size, maze_y_offset + goal_position[1] * tile_size, tile_size, tile_size))

def check_win():
    return player_position == goal_position

# Game loop setup
clock = pygame.time.Clock()
running = True

while running:
    if vision_radius <= 0:
        screen.fill(BLACK)
        font = pygame.font.SysFont('Arial', 40)
        game_over_text = font.render("Game Over! You lost your vision.", True, RED)
        screen.blit(game_over_text, (screen_w // 2 - game_over_text.get_width() // 2, screen_h // 2 - game_over_text.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False
        continue

    screen.fill(BLACK)
    draw_maze()
    draw_player()
    draw_goal()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_LEFT] and player_position[0] > 0 and maze[player_position[1]][player_position[0] - 1] == 0:
        player_position[0] -= 1
        moved = True
    if keys[pygame.K_RIGHT] and player_position[0] < len(maze[0]) - 1 and maze[player_position[1]][player_position[0] + 1] == 0:
        player_position[0] += 1
        moved = True
    if keys[pygame.K_UP] and player_position[1] > 0 and maze[player_position[1] - 1][player_position[0]] == 0:
        player_position[1] -= 1
        moved = True
    if keys[pygame.K_DOWN] and player_position[1] < len(maze) - 1 and maze[player_position[1] + 1][player_position[0]] == 0:
        player_position[1] += 1
        moved = True

    if moved:
        vision_radius = max(0, vision_radius - 0.2)

    if check_win():
        screen.fill(BLACK)
        font = pygame.font.SysFont('Arial', 40)
        win_text = font.render("You Escaped!", True, GREEN)
        screen.blit(win_text, (screen_w // 2 - win_text.get_width() // 2, screen_h // 2 - win_text.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False

    pygame.display.flip()
    clock.tick(15)

pygame.quit()
sys.exit()
