
import pygame
import heapq
import random
from collections import deque

pygame.init()

# Grid settings
ROWS = 20
COLS = 20
CELL_SIZE = 35

GRID_WIDTH = COLS * CELL_SIZE
GRID_LENGTH = ROWS * CELL_SIZE


WIDTH = GRID_WIDTH * 2
LENGGRID_LENGTH = GRID_LENGTH + 65

FPS = 60
ANIMATION_SPEED = 3
DENSITY =0.3

screen = pygame.display.set_mode((WIDTH, LENGGRID_LENGTH))
pygame.display.set_caption("A* Pathfinding Visualizer")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
small_font= pygame.font.SysFont(None, 23)


# Colors
WHITE = (255, 255, 255)
BLACK = (40, 40, 40)
GREY = (180, 180, 180)
GREEN = (0, 200, 80)
RED = (220, 50, 50)
BLUE = (60, 130, 255)
YELLOW = (255, 205, 60)
PURPLE = (180, 120, 240)

obstacles = set()
start = None
end = None
bfs_path = None
astar_path = None

bfs_explored = []
astar_explored = []

animation_step = 0
animating = False

bfs_nodes = 0
astar_nodes = 0

# Manhattan distance heuristic
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# Find valid neighbouring cells
def get_neighbours(current):
    row, col = current

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    neighbours = []

    for dr, dc in directions:
        new_row = row + dr
        new_col = col + dc

        if 0 <= new_row < ROWS and 0 <= new_col < COLS:
            neighbour = (new_row, new_col)

            if neighbour not in obstacles:
                neighbours.append(neighbour)

    return neighbours


# A* algorithm
def solve(start, goal):
    frontier = []
    heapq.heappush(frontier, (0, start))
    

    came_from = {start: None}
    cost_so_far = {start: 0}

    explored_order = []
    expanded = set()

    while frontier:
        priority, current = heapq.heappop(frontier)

        if current in expanded:
            continue

        if priority > cost_so_far[current] + heuristic(current, goal):
            continue

        expanded.add(current)
        explored_order.append(current)

        if current == goal:
            break

        for neighbour in get_neighbours(current):
            new_cost = cost_so_far[current] + 1

            if neighbour not in cost_so_far or new_cost < cost_so_far[neighbour]:
                cost_so_far[neighbour] = new_cost
                came_from[neighbour] = current

                priority = new_cost + heuristic(goal, neighbour)
                heapq.heappush(frontier, (priority, neighbour))

    return came_from, cost_so_far, explored_order

def bfs(start, goal):
    frontier = deque([start])

    came_from = {start: None}

    explored_order = []

    while frontier:
        current = frontier.popleft()
        explored_order.append(current)


        if current == goal:
            break

        for neighbour in get_neighbours(current):
            if neighbour not in came_from:
                came_from[neighbour] = current
                frontier.append(neighbour)

    return came_from, explored_order
# Reconstruct shortest path
def reconpath(start, end, came_from):
    if end not in came_from:
        return None

    path = []
    current = end

    while current is not None:
        path.append(current)
        current = came_from[current]

    path.reverse()

    if path[0] != start:
        return None

    return path


def reset_search():
    global bfs_path, astar_path
    global bfs_explored, astar_explored
    global animation_step, animating
    global bfs_nodes, astar_nodes

    bfs_path = None
    astar_path = None

    bfs_explored = []
    astar_explored = []

    animation_step = 0
    animating = False

    bfs_nodes = 0
    astar_nodes = 0


def generate_maze():
    if start is None or end is None:
        print("Select a start and end first!")
        return
    
    for attempts in range (200):
        obstacles.clear()

        for row in range(ROWS):
            for col in range(COLS):
                cell = (row, col)

                if cell == start or cell == end:
                    continue

                if random.random() < DENSITY:
                    obstacles.add(cell)

        came_from, _,_ = solve(start, end)

        if end in came_from:
            print("Solvable maze generated!")
            reset_search()
            break

def run_comparison():
    global bfs_path, astar_path
    global bfs_explored, astar_explored
    global bfs_nodes, astar_nodes
    global animation_step, animating

    if start is None or end is None:
        print("Select start and end first!")
        return

    bfs_came_from, bfs_explored = bfs(start, end)

    astar_came_from, _, astar_explored = solve(start, end)

    bfs_path = reconpath(start, end, bfs_came_from)
    astar_path = reconpath(start, end, astar_came_from)

    bfs_nodes = len(bfs_explored)
    astar_nodes = len(astar_explored)

    animation_step = 0
    animating = True

    print("\n--- COMPARISON ---")

    print("BFS nodes explored:", bfs_nodes)
    print("A* nodes explored:", astar_nodes)

    if bfs_path is not None:
        print("BFS path length:", len(bfs_path) - 1)
    else:
        print("BFS: No path found")

    if astar_path is not None:
        print("A* path length:", len(astar_path) - 1)
    else:
        print("A*: No path found")

def draw_grid(offset_x, explored, path, color):
    visible_explored = set(explored[:animation_step])

    # Show final path only when this
    # algorithm finishes its exploration.
    finished = animation_step >= len(explored)

    visible_path = set(path) if finished and path else set()

    for row in range(ROWS):
        for col in range(COLS):
            cell = (row, col)

            rect = pygame.Rect(
                col * CELL_SIZE + offset_x,
                row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )

            if cell in obstacles:
                pygame.draw.rect(screen, BLACK, rect)

            elif cell in visible_path:
                pygame.draw.rect(screen, BLUE, rect)

            elif cell in visible_explored:
                pygame.draw.rect(screen, color, rect)

            if cell == start:
                pygame.draw.rect(screen, GREEN, rect)

            elif cell == end:
                pygame.draw.rect(screen, RED, rect)

            pygame.draw.rect(screen, GREY, rect, 1)


# Main Pygame loop

running = True

while running:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Mouse input
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            if y < GRID_LENGTH:
                col = (x // CELL_SIZE) % COLS
                row = y // CELL_SIZE
                cell = (row, col)

                if event.button == 1:
                    if start is None:
                        start = cell

                    elif end is None and cell != start:
                        end = cell

                    elif cell != start and cell != end:
                        obstacles.add(cell)

                    reset_search()

                elif event.button == 3:
                    obstacles.discard(cell)

                    if cell == start:
                        start = None

                    if cell == end:
                        end = None

                    reset_search()

        # Keyboard input
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:
                run_comparison()

            elif event.key == pygame.K_o:
                generate_maze()

            elif event.key == pygame.K_c:
                obstacles.clear()
                start = None
                end = None
                reset_search()

    # Advance both animations together
    if animating:
        animation_step += ANIMATION_SPEED

        if animation_step >= max(
            len(bfs_explored),
            len(astar_explored)
        ):
            animating = False

    # Draw everything
    screen.fill(WHITE)

    # Left: BFS
    draw_grid(
        0,
        bfs_explored,
        bfs_path,
        YELLOW
    )

    # Right: A*
    draw_grid(
        GRID_WIDTH,
        astar_explored,
        astar_path,
        PURPLE
    )

    # Bottom statistics panel
    pygame.draw.rect(
        screen,
        (235, 235, 235),
        (0, GRID_LENGTH, WIDTH, 65)
    )

    bfs_label = font.render(
        f"BFS | Explored: {min(animation_step, bfs_nodes)}/{bfs_nodes}",
        True,
        BLACK
    )

    astar_label = font.render(
        f"A* | Explored: {min(animation_step, astar_nodes)}/{astar_nodes}",
        True,
        BLACK
    )

    screen.blit(bfs_label, (15, GRID_LENGTH + 8))
    screen.blit(astar_label, (GRID_WIDTH + 15, GRID_LENGTH + 8))

    instructions = small_font.render(
        "SPACE: Compare    O: Random maze    C: Clear    Left-click: Add    Right-click: Remove",
        True,
        BLACK
    )

    screen.blit(instructions, (15, GRID_LENGTH + 38))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()