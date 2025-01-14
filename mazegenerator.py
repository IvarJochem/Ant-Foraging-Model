import random
import numpy as np

# Initialize the maze with all walls as 2s
def initialize_maze(rows, cols):
    maze = np.array([[2] * cols for _ in range(rows)])
    return maze

# Recursive function to carve passages in the maze
def carve_passages_from(cx, cy, maze, rows, cols):
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    random.shuffle(directions)
    # Try each direction
    for direction in directions:
        nx, ny = cx + direction[0] * 2, cy + direction[1] * 2
        # Check if the new cell is within bounds and not visited
        if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] == 2:
            maze[cx + direction[0]][cy + direction[1]] = 0
            maze[nx][ny] = 0
            carve_passages_from(nx, ny, maze, rows, cols)

def generate_maze(rows, cols):
    maze = initialize_maze(rows, cols)
    start_x, start_y = 1, 1
    maze[start_x][start_y] = 0
    carve_passages_from(start_x, start_y, maze, rows, cols)
    return maze

def print_maze(maze):
    for row in maze:
        print(" ".join(str(cell) for cell in row))

if __name__ == "__main__":
    rows, cols = 11, 11  # Dimensions of the maze (must be odd numbers)
    maze = generate_maze(rows, cols)
    print_maze(maze)
