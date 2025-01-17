import numpy as np
import matplotlib.pyplot as plt
from mazegenerator import generate_maze, upscale_maze


class Model:
    def __init__(self, Maze, width, height, nAnts=10):
        """
        Initialize the model with width, height, and number of ants.
        """
        self.width = width
        self.height = height
        self.nAnts = nAnts

        # Our grid is a maze with walls (2) and open spaces (0)
        self.grid = Maze

        # We initialize colony in the center and the food at the top
        self.colony_position = (4, 4)
        self.food_position = (len(Maze[0])-6, len(Maze)-6)

        # Colony is represented as a -1 and food as a 1
        self.grid[self.colony_position] = -1
        self.grid[self.food_position] = 1

        # Initialize ants at the colony
        self.ants = [Ant(Maze, self.colony_position[0], self.colony_position[1]) for _ in range(nAnts)]

    def update(self):
        """
        Update the positions of all ants and stop if food is found.
        """
        food_found = False
        for ant in self.ants:
            ant.step(0.1)  # Update position and direction
            # Check if an ant has found the food
            if (int(ant.position[0]), int(ant.position[1])) == self.food_position:
                food_found = True
        return food_found


class Ant:
    def __init__(self, Maze, x, y):
        """
        Class to model the ants. Each ant is initialized with a position and direction.
        """
        self.position = [x, y]
        self.colony_position = [x, y]
        self.has_moved_away = False
        self.grid = Maze
        self.visited = []
        self.visited.append(self.position)
        self.path = []
        self.path.append(self.position)
        self.time_since_last_update = 0.0

    def get_adjacent_cells(self):
        """
        Get the adjacent cells of the ant in the grid.
        """
        x, y = self.position
        adj_cells = [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
        return adj_cells

    def shuffle_cells_with_bias(self, adj_cells, bias=0.8):
        """
        Shuffle the adjacent cells with a bias to move away from the colony.
        Bias is the probability of moving away from the colony.
        """
        if np.random.rand() > bias:
            np.random.shuffle(adj_cells)
        else:
            distances = [np.linalg.norm(np.array(cell) - np.array(self.colony_position)) for cell in adj_cells]
            adj_cells = [cell for _, cell in sorted(zip(distances, adj_cells))]
            adj_cells.reverse()
        return adj_cells

    def step(self, dt):
        """Update the ant's state for the given time step."""
        self.time_since_last_update += dt
        if self.time_since_last_update > 0.0:
            # check adjacent cells for cells that the ant has not visited
            # and move to the cell that has not been visited
            adj_cells = self.get_adjacent_cells()
            # shuffle the adjacent cells to randomize the movement
            adj_cells = self.shuffle_cells_with_bias(adj_cells)
            for cell in adj_cells:
                if self.grid[int(cell[0]), int(cell[1])] != 2 and cell not in self.visited:
                    self.position = cell
                    # change the cell to -3 to visualize that the ant has visited the cell
                    Maze[int(cell[0]), int(cell[1])] = -3
                    self.visited.append(self.position)
                    self.path.append(self.position)
                    self.time_since_last_update = 0.0
                    return

            # if all adjacent cells have been visited, move back to the previous cell
            self.position = self.path[-2]
            self.path.pop()
            # print(f"Backtracking to {self.position}")
            self.time_since_last_update = 0.0
            return


class Visualization:
    def __init__(self, Maze, height, width, pauseTime=0.01):
        """
        This simple visualization shows the colony, food, and ants.
        """
        self.h = height
        self.w = width
        self.pauseTime = pauseTime
        grid = Maze.copy()
        self.im = plt.imshow(grid, vmin=-3, vmax=2, cmap='rainbow')
        plt.title('Ant Simulation')

    def update(self, t, colony_position, food_position, ant_positions):
        """
        Updates the grid with colony, food, and ants for visualization.
        """
        grid = Maze.copy()

        # # Visualize the colony with a 3x3 radius in yellow (-1)
        # for dx in [-1, 0, 1]:
        #     for dy in [-1, 0, 1]:
        #         x = (colony_position[0] + dx) % self.h
        #         y = (colony_position[1] + dy) % self.w
        #         grid[x, y] = -1

        # # Visualize the food (2)
        # grid[food_position[0], food_position[1]] = 2

        # Visualize the ants (-2)
        for x, y in ant_positions:
            grid[int(x), int(y)] = -2

        self.im.set_data(grid)

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
    timeSteps = 1000
    t = 0
    Maze = generate_maze(21, 21)
    Maze = upscale_maze(Maze, 3)
    sim = Model(Maze, len(Maze[0]), len(Maze))
    vis = Visualization(Maze, sim.height, sim.width)
    print('Starting simulation')
    while t < timeSteps:
        food_found = sim.update()  # Update simulation
        ant_positions = [ant.position for ant in sim.ants]
        vis.update(t, sim.colony_position, sim.food_position, ant_positions)
        if food_found:
            print(f"Food found at timestep {t}!")
            break
        t += 1
    vis.persist()
