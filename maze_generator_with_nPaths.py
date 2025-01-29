import random
import numpy as np

# Initialize the maze with all walls
def initialize_maze(rows, cols):
    maze = np.array([[2] * cols for _ in range(rows)])
    return maze

# Recursive function to carve passages in the maze
def carve_passages_from(cx, cy, maze, rows, cols, path_count, current_paths):
    """Function that generates paths until path count is reached"""
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    random.shuffle(directions)
    # Try each direction
    for direction in directions:
        nx, ny = cx + direction[0] * 2, cy + direction[1] * 2
        # Check if the new cell is within bounds and not visited
        if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] == 2:
            maze[cx + direction[0]][cy + direction[1]] = 0
            maze[nx][ny] = 0
            # Recursively carve passages from the new cell
            carve_passages_from(nx, ny, maze, rows, cols, path_count, current_paths)

    # Add extra paths after the main recursive call
    if current_paths[0] < path_count:
        for direction in directions:
            nx, ny = cx + direction[0] * 2, cy + direction[1] * 2
            if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] == 0:
                # Randomly add a connection to create more paths 
                # (probability can be changed / seed can be set)
                if random.random() < 0.5:
                    maze[cx + direction[0]][cy + direction[1]] = 0
                    current_paths[0] += 1
                    if current_paths[0] >= path_count:
                        return

def generate_maze_with_paths(rows, cols, path_count, randomseed=1275832698236592):
    """Function that generates maze"""
    maze = initialize_maze(rows, cols)
    start_x, start_y = 1, 1
    maze[start_x][start_y] = 0
    random.seed(randomseed)
    # Track the number of paths created
    current_paths = [1]
    carve_passages_from(start_x, start_y, maze, rows, cols, path_count, current_paths)
    return maze

def upscale_maze(maze, scale):
    rows, cols = maze.shape
    upscaled_maze = np.zeros((rows * scale, cols * scale))
    for i in range(rows):
        for j in range(cols):
            upscaled_maze[i * scale:(i + 1) * scale, j * scale:(j + 1) * scale] = maze[i][j]
    return upscaled_maze

def print_maze(maze):
    for row in maze:
        print(" ".join(str(cell) for cell in row))

if __name__ == "__main__":
    rows, cols = 11, 11  # Dimensions of the maze (must be odd numbers)
    path_count = 32  # Change this to 120, 55, 32, or 16
    maze = generate_maze_with_paths(rows, cols, path_count)
    print_maze(maze)
