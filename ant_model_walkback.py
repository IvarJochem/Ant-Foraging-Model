
import numpy as np
import matplotlib.pyplot as plt
from maze_generator_with_nPaths import generate_maze_with_paths, upscale_maze

# Number of paths change this to 120, 55, 32, or 16
nPaths = 32

# Number of time steps in the simulation 
ntimeSteps = 2500

# Maze dimention, must be odd number 
maze_dimention = 21

# Maze scale (the width of the paths)
maze_scale = 2

# Maze size
maze_size = maze_dimention*maze_scale

# Colony position
colony_position = (maze_scale, maze_scale)

# Food position
food_position = (maze_size-maze_scale-1, maze_size-maze_scale-1)

# Number of ants
nAnts = 250

# Number of ants per wave
nWaveAnts = 1

# Time step between waves
WaveTimesteps = 1

# Number of ants that have to return with food 
ants_with_food_returned = 1000

# Maximum amount of pheromone deposited per timestep per ant
pheromone_deposit = 0.3

#Strength of decay 
decay_strength = 1 

# Base chance of choosing a cell
base_chance = 0.7

# Decay rate of pheromones
decay_rate = 0.02

# Maximum amount of pheromones per cell
max_pheromone = 0.99

# Cell types
colony = -1
open_space = 0
food = 1
wall = 2


class Model:
    def __init__(self, maze, width, height):
        """
        Initialize the model with width, height, and number of ants.
        """
        self.width = width
        self.height = height
        self.nAnts = nAnts
        self.nWaveAnts = nWaveAnts
        self.WaveTimesteps = WaveTimesteps
        self.total_ants_spawned = 0

        # Our grid is a maze with walls (2) and open spaces (0)
        self.grid = maze

        # We initialize colony in the top left and the food at the bottom right
        self.colony_position = colony_position
        self.food_position = food_position

        # Colony is represented as a -1 and food as a 1
        self.grid[self.colony_position] = colony
        self.grid[self.food_position] = food
        # Initialize pheromone grid
        self.pheromones = np.zeros_like(maze, dtype = float)
        # Initialize ants at the colony
        self.ants = []

        # Track the food deliverd
        self.food_found = 0

        # Track if food is discovered
        self.food_discovered = False

    def spawn_ants(self):
        """
        Spawn a wave of ants if the maximum number of ants has not been reached.
        """
        if self.total_ants_spawned < self.nAnts:
            new_ants = min(self.nWaveAnts, self.nAnts - self.total_ants_spawned)
            for _ in range(new_ants):
                self.ants.append(Ant(self.grid, self.pheromones, self.colony_position))
            self.total_ants_spawned += new_ants

    def update(self, timestep):
        """
        Update the positions of all ants and stop if food is found.
        """
        if timestep % self.WaveTimesteps == 0:
            self.spawn_ants()

        self.pheromones *= (1-decay_rate)
        for ant in self.ants:
            ant.step(0.1)  # Update position and direction
            # Check if an ant has found the food
            if ant.hasfood and (ant.position[0], ant.position[1]) == self.colony_position:
                self.food_discovered = True
                self.food_found += 1  # Increment the food delivered count
                ant.hasfood = False
                ant.visited = {}
                ant.visited[str(ant.position)] = True
                ant.path = []
                ant.path.append(ant.position)
                ant.time_since_last_update = 0.0


class Ant:
    def __init__(self, maze, pheromones, colony_position):
        """
        Class to model the ants. Each ant is initialized with a position and direction.
        """
        self.position = colony_position
        self.colony_position = colony_position
        self.has_moved_away = False
        self.grid = maze
        self.visited = {}
        self.visited[str(self.position)] = True
        self.path = []
        self.path.append(self.position)
        self.final_path_length = 0
        self.time_since_last_update = 0.0
        self.hasfood = False
        self.pheromones = pheromones

    def get_adjacent_cells(self):
        """
        Get the adjacent cells of the ant in the grid.
        """
        x, y = self.position
        adj_cells = [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
        return adj_cells

    def choose_cells_based_on_pheromones(self, adj_cells):
        """
        Choose one of adjecent cells based on pheromone level
        """
        # remove cells that are walls
        adj_cells = [cell for cell in adj_cells if self.grid[cell[0], cell[1]] != wall]
        # remove cells that are visited
        adj_cells = [cell for cell in adj_cells if str(cell) not in self.visited.keys()]

        if len(adj_cells) == 0:
            return False

        total_chance = 0
        for cell in adj_cells:
            total_chance += self.pheromones[cell[0], cell[1]] + base_chance

        if total_chance == len(adj_cells)*base_chance:
            # nothing happens, no pheromones
            np.random.shuffle(adj_cells)
            return adj_cells[0]
        # pick a random number between 0 and the total pheromones
        pheromone_pick  = np.random.uniform(0, total_chance)
        current_chance = 0
        # pick the cell based on pheromone_pick
        for cell in adj_cells:
            current_chance += self.pheromones[cell[0], cell[1]] + base_chance
            if current_chance >= pheromone_pick:
                return cell

        return False

    def step(self, dt):
        """Update the ant's state for the given time step."""
        self.time_since_last_update += dt
        x, y = self.position
        current_cell_value = self.grid[x, y]
        # check if the ant found food
        if current_cell_value == food:
            self.hasfood = True

        if self.hasfood:
            if self.position == self.colony_position:
                self.hasfood = False
                self.visited = {}
                self.visited[str(self.position)] = True
                self.path = []
                self.path.append(self.position)
                return
            elif current_cell_value == food:
                self.final_path_length = len(self.path)
            elif current_cell_value >= 0 and current_cell_value < 1:
                current_pheromone_deposit = pheromone_deposit*(((len(self.path)/self.final_path_length) / decay_strength)**2)
                self.pheromones[x, y] = min(self.pheromones[x, y] +  current_pheromone_deposit , max_pheromone)
        else:
            adj_cells = self.get_adjacent_cells()
            # choose the next cell based on pheromones
            cell = self.choose_cells_based_on_pheromones(adj_cells)
            if cell != False:
                self.position = cell
                self.visited[str(self.position)] = True
                self.path.append(self.position)
                self.time_since_last_update = 0.0
                return
        # move back to the colony along the path
        self.path.pop()
        if len(self.path) > 0:
            self.position = self.path[-1]
        self.time_since_last_update = 0.0
        return

class Visualization:
    def __init__(self, maze, pheromones, height, width, pauseTime=0.01):
        """
        This visualization uses separate scatter plots for ants to preserve colony and food colors.
        """
        self.h = height
        self.w = width
        self.pauseTime = pauseTime
        self.grid = maze.copy()
        self.pheromones = pheromones
        from matplotlib.colors import ListedColormap
        colors = [
            "yellow",  # -1 colony
            "white",   # 0 open spaces
            "green",   # 1 food
            "black",   # 2 walls
        ]
        # Adjusted color indices to match the grid values
        custom_cmap = ListedColormap(colors)
        self.im = plt.imshow(self.grid, vmin=-1, vmax=2, cmap=custom_cmap)

        # Initialize scatter plots for ants
        self.ants_without_food_scatter = plt.scatter([], [], color='red', marker='o', s=25, zorder=3)
        self.ants_with_food_scatter = plt.scatter([], [], color='purple', marker='o', s=25, zorder=3)

        self.ph_im = None
        plt.title('Ant Simulation')

    def update(self, t, ant_without_food_positions, ant_with_food_positions):
        """
        Updates the visualization with pheromones and ant positions using scatter plots.
        """
        # Update pheromones overlay
        if self.ph_im is None:
            self.ph_im = plt.imshow(self.pheromones, alpha=0.5, cmap='hot', vmin=0, vmax=max_pheromone)
        else:
            self.ph_im.set_data(self.pheromones)

        # Update ant positions
        # Convert positions to (x, y) coordinates for scatter plot (inverting rows and columns)
        if ant_without_food_positions:
            x_no_food = [y + 0.5 for x, y in ant_without_food_positions]
            y_no_food = [x + 0.5 for x, y in ant_without_food_positions]
            self.ants_without_food_scatter.set_offsets(np.column_stack((x_no_food, y_no_food)))
        else:
            # Use empty 2D array when no positions
            self.ants_without_food_scatter.set_offsets(np.empty((0, 2)))

        if ant_with_food_positions:
            x_with_food = [y + 0.5 for x, y in ant_with_food_positions]
            y_with_food = [x + 0.5 for x, y in ant_with_food_positions]
            self.ants_with_food_scatter.set_offsets(np.column_stack((x_with_food, y_with_food)))
        else:
            # Use empty 2D array when no positions
            self.ants_with_food_scatter.set_offsets(np.empty((0, 2)))

        plt.title('t = %i' % t)
        plt.draw()
        plt.pause(self.pauseTime)

    def persist(self):
        plt.show()


if __name__ == '__main__':
    """
    Simulation parameters
    """
    import time
    timeSteps = ntimeSteps
    t = 0
    maze = generate_maze_with_paths(maze_dimention, maze_dimention, nPaths)
    maze = upscale_maze(maze, maze_scale)
    sim = Model(maze, len(maze[0]), len(maze))
    vis = Visualization(maze, sim.pheromones, sim.height, sim.width)
    print('Starting simulation')
    while t < timeSteps and not sim.food_found > ants_with_food_returned -1:
        food_found = sim.update(t)  # Update simulation
        ant_without_food_positions = [ant.position for ant in sim.ants if not ant.hasfood]
        ant_with_food_positions = [ant.position for ant in sim.ants if ant.hasfood]
        vis.update(t, ant_without_food_positions, ant_with_food_positions)
        t += 1
    vis.persist()