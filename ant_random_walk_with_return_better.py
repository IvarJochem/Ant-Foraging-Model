import numpy as np
import matplotlib.pyplot as plt
from collections import deque

class Model:
    def __init__(self, width=80, height=80, nAnts=1000, case=1):
        """
        Initialize the model with width, height, and number of ants.
        case parameter determines the maze layout.
        """
        self.width = width
        self.height = height
        self.nAnts = nAnts
        self.case = case

        # Initialize grid and set up maze based on case
        self.grid = self.initialize_maze(case)
        
        # Calculate distance maps for both food and colony
        self.distance_map_food = self.calculate_distance_map(self.food_position)
        self.distance_map_colony = self.calculate_distance_map(self.colony_position)

        # Initialize ants
        self.ants = [Ant(*self.colony_position, self.colony_position, self.food_position) 
                    for _ in range(nAnts)]

    def calculate_distance_map(self, target):
        """
        Creates a distance map using flood fill algorithm from the target position.
        Returns a grid where each cell contains the shortest distance to the target avoiding walls.
        """
        distance_map = np.full((self.height, self.width), np.inf)
        distance_map[target] = 0
        queue = deque([target])
        visited = set([target])
        
        # Possible movements (including diagonals)
        directions = [(dx, dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if dx != 0 or dy != 0]
        
        while queue:
            current = queue.popleft()
            current_distance = distance_map[current]
            
            for dx, dy in directions:
                next_x, next_y = current[0] + dx, current[1] + dy
                
                # Check boundaries and walls
                if (0 <= next_x < self.height and 
                    0 <= next_y < self.width and 
                    self.grid[next_x, next_y] != 4 and  # Not a wall
                    (next_x, next_y) not in visited):
                    
                    # Calculate new distance (use 1.4 for diagonal moves, 1 for orthogonal)
                    move_cost = 1.4 if dx != 0 and dy != 0 else 1
                    new_distance = current_distance + move_cost
                    
                    if new_distance < distance_map[next_x, next_y]:
                        distance_map[next_x, next_y] = new_distance
                        queue.append((next_x, next_y))
                        visited.add((next_x, next_y))
        
        return distance_map

    def initialize_maze(self, case):
        """
        Initialize the grid with walls based on the case number.
        Wall cells have value 4
        """
        grid = np.zeros((self.height, self.width))
        
        if case == 1:
            # Case 1: Original setup with no walls
            self.colony_position = (self.height - 5, self.width // 2)
            self.food_position = (4, self.width // 2)
            
        elif case == 2:
            # Case 2: Simple wall in the middle
            self.colony_position = (self.height - 5, self.width // 2)
            self.food_position = (4, self.width // 2)
            
            # Add horizontal wall in the middle with gaps on both ends
            wall_y = self.height // 2
            wall_start = self.width // 4
            wall_end = (3 * self.width) // 4
            
            grid[wall_y, wall_start:wall_end] = 4
            
        elif case == 3:
            # Case 3: Maze with multiple walls
            self.colony_position = (self.height - 5, self.width // 2)
            self.food_position = (4, self.width // 2)
            
            # Add multiple horizontal walls with gaps at different positions
            wall_positions = [self.height // 4, self.height // 2, (3 * self.height) // 4]
            gap_positions = [self.width // 4, self.width // 2, (3 * self.width) // 4]
            
            for wall_y, gap_x in zip(wall_positions, gap_positions):
                grid[wall_y, :gap_x-5] = 4
                grid[wall_y, gap_x+5:] = 4

        # Set colony and food positions
        grid[self.colony_position] = -1
        grid[self.food_position] = 1
        
        return grid

    def update(self):
        """
        Update the positions of all ants and handle food collection/delivery.
        """
        for ant in self.ants:
            ant.move(self.height, self.width, self.grid, 
                    self.distance_map_food, self.distance_map_colony)
            
            # Check if ant found food
            if tuple(ant.position) == self.food_position and not ant.has_food:
                ant.has_food = True
                ant.state = 'returning'
                print(f"Ant found food!")
                
            # Check if ant returned to colony with food
            elif tuple(ant.position) == self.colony_position and ant.has_food:
                ant.has_food = False
                ant.state = 'foraging'
                print(f"Ant returned food to nest!")

class Ant:
    def __init__(self, x, y, colony_pos, food_pos):
        """
        Initialize an ant with starting position and target locations
        """
        self.position = [x, y]
        self.colony_pos = colony_pos
        self.food_pos = food_pos
        self.state = 'foraging'
        self.has_food = False
        self.food_bias = 0.3

    def valid_moves(self, height, width, grid):
        """
        Returns list of valid moves, excluding walls
        """
        moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    new_x = self.position[0] + dx
                    new_y = self.position[1] + dy
                    if (0 <= new_x < height and 0 <= new_y < width and 
                        grid[int(new_x), int(new_y)] != 4):
                        moves.append((new_x, new_y))
        return moves

    def get_best_move(self, moves, distance_map):
        """
        Returns the move that leads to the shortest path based on the distance map
        """
        best_move = None
        min_distance = float('inf')
        
        for move in moves:
            distance = distance_map[int(move[0]), int(move[1])]
            if distance < min_distance:
                min_distance = distance
                best_move = move
        
        return best_move if best_move is not None else moves[0]

    def move(self, height, width, grid, distance_map_food, distance_map_colony):
        """
        Moves the ant based on its state and the appropriate distance map
        """
        moves = self.valid_moves(height, width, grid)
        
        if not moves:
            return
            
        if self.state == 'returning':
            # Use colony distance map when returning
            best_move = self.get_best_move(moves, distance_map_colony)
            self.position = list(best_move)
        else:  # foraging state
            if np.random.random() < self.food_bias:
                # Use food distance map when moving towards food
                best_move = self.get_best_move(moves, distance_map_food)
                self.position = list(best_move)
            else:
                # Random movement
                self.position = list(moves[np.random.randint(len(moves))])

class Visualization:
    def __init__(self, height, width, pauseTime=0.01):
        """
        Initialize visualization with matplotlib
        """
        self.h = height
        self.w = width
        self.pauseTime = pauseTime
        grid = np.zeros((self.w, self.h))
        self.im = plt.imshow(grid, vmin=-1, vmax=4, cmap='rainbow')
        plt.title('Ant Simulation')

    def update(self, t, colony_position, food_position, ants, grid):
        """
        Updates the grid with colony, food, walls, and ants for visualization
        """
        display_grid = grid.copy()

        # Visualize the colony
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                x = (colony_position[0] + dx) % self.h
                y = (colony_position[1] + dy) % self.w
                if display_grid[x, y] != 4:  # Don't overwrite walls
                    display_grid[x, y] = -1

        # Visualize the food
        display_grid[food_position[0], food_position[1]] = 1

        # Visualize the ants
        for ant in ants:
            x, y = int(ant.position[0]), int(ant.position[1])
            if display_grid[x, y] != 4:  # Don't overwrite walls
                display_grid[x, y] = 3 if ant.has_food else 2

        self.im.set_data(display_grid)
        plt.draw()
        plt.title(f't = {t}')
        plt.pause(self.pauseTime)

    def persist(self):
        plt.show()

if __name__ == '__main__':
    """
    Main simulation parameters and run
    """
    timeSteps = 1000
    t = 0
    
    # Choose case (1, 2, or 3)
    case = 3
    
    sim = Model(case=case)
    vis = Visualization(sim.height, sim.width)
    print(f'Starting simulation - Case {case}')
    
    while t < timeSteps:
        sim.update()
        vis.update(t, sim.colony_position, sim.food_position, sim.ants, sim.grid)
        t += 1
    vis.persist()