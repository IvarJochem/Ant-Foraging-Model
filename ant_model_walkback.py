
import numpy as np
import matplotlib.pyplot as plt
from maze_generator_with_nPaths import generate_maze_with_paths, upscale_maze

# Number of paths change this to 120, 55, 32, or 16
nPaths = 16

# Number of time steps in the simulation 
ntimeSteps = 1000

# Maze dimention, must be odd number 
maze_dimention = 13

# Maze scale (the width of the paths)
maze_scale = 3

# Maze size
maze_size = maze_dimention*maze_scale

# Number of ants
nAnts = 100

# Number of ants that have to return with food 
ants_with_food_returned = 50

# Amount of pheromone deposited per timestep per ant
pheromone_deposit = 0.1

# Decay rate of pheromones
decay_rate = 0.01

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

        # Our grid is a maze with walls (2) and open spaces (0)
        self.grid = maze

        # We initialize colony in the top left and the food at the bottom right
        self.colony_position = (maze_scale, maze_scale)
        self.food_position = (maze_size-maze_scale-1, maze_size-maze_scale-1)

        # Colony is represented as a -1 and food as a 1
        self.grid[self.colony_position] = colony
        self.grid[self.food_position] = food
        # Initialize pheromone grid
        self.pheromones = np.zeros_like(maze, dtype = float)
        # Initialize ants at the colony
        self.ants = [Ant(maze, self.pheromones, self.colony_position) for _ in range(nAnts)]

        # Track the food deliverd
        self.food_found = 0

        # Track if food is discovered
        self.food_discovered = False

    def update(self):
        """
        Update the positions of all ants and stop if food is found.
        """
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
            total_chance += self.pheromones[cell[0], cell[1]] + 0.1

        if total_chance == len(adj_cells)*0.1:
            # nothing happens, no pheromones
            np.random.shuffle(adj_cells)
            return adj_cells[0]
        # pick a random number between 0 and the total pheromones
        pheromone_pick  = np.random.uniform(0, total_chance)
        current_chance = 0
        # pick the cell based on pheromone_pick
        for cell in adj_cells:
            current_chance += self.pheromones[cell[0], cell[1]] + 0.1
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
            else:
                if current_cell_value >= 0 and current_cell_value < 1:
                    self.pheromones[x, y] = min(self.pheromones[x, y] +  pheromone_deposit , max_pheromone)
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
        This simple visualization shows the colony, food, and ants.
        """
        self.h = height
        self.w = width
        self.pauseTime = pauseTime
        self.grid = maze.copy()
        self.pheromones = pheromones
        from matplotlib.colors import ListedColormap
        colors = [
            "purple", # -3 ants with food
            "red", # -2 ants no food
            "yellow", #-1 colony
            "white", # 0 open spaces
            "green", # 1 food
            "black", # 2 walls

        ]
        custom_cmap = ListedColormap(colors)

        self.im = plt.imshow(self.grid, vmin=-3, vmax=3, cmap=custom_cmap)

        self.ph_im = None
        plt.title('Ant Simulation')

    def update(self, t, ant_without_food_positions, ant_with_food_positions):
        """
        Updates the grid with colony, food, and ants for visualization.
        """
        self.grid = maze.copy()

        # Visualize the pheromones
        if self.ph_im is None:
            self.ph_im = plt.imshow(self.pheromones, alpha=0.5, cmap='hot', vmin=0, vmax=max_pheromone)
        else:
            self.ph_im.set_data(self.pheromones)
        # # Visualize the colony with a 3x3 radius in yellow (-1)
        # for dx in [-1, 0, 1]:
        #     for dy in [-1, 0, 1]:
        #         x = (colony_position[0] + dx) % self.h
        #         y = (colony_position[1] + dy) % self.w
        #         grid[x, y] = -1

        # # Visualize the food (2)
        # grid[food_position[0], food_position[1]] = 2

        # Visualize the ants (-2)
        for x, y in ant_without_food_positions:
            self.grid[x, y] = -2

        # Visualize the ants with food (-3)
        for x, y in ant_with_food_positions:
            self.grid[x, y] = -3

        self.im.set_data(self.grid)

        plt.draw()
        plt.title('t = %i' % t)
        plt.pause(self.pauseTime)

    def persist(self):
        """
        Use this method if you want to have the visualization persist after the
        calling the update method for the last time.
        """
        plt.show()


if __name__ == '__main__':
    """
    Simulation parameters
    """
    timeSteps = ntimeSteps
    t = 0
    maze = generate_maze_with_paths(maze_dimention, maze_dimention, nPaths)
    maze = upscale_maze(maze, maze_scale)
    sim = Model(maze, len(maze[0]), len(maze))
    vis = Visualization(maze, sim.pheromones, sim.height, sim.width)
    print('Starting simulation')
    while t < timeSteps and not sim.food_found > ants_with_food_returned -1:
        food_found = sim.update()  # Update simulation
        ant_without_food_positions = [ant.position for ant in sim.ants if not ant.hasfood]
        ant_with_food_positions = [ant.position for ant in sim.ants if ant.hasfood]
        vis.update(t, ant_without_food_positions, ant_with_food_positions)
        t += 1
    vis.persist()
