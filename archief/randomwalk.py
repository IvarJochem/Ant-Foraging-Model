import numpy as np
import matplotlib.pyplot as plt

class Model:
    def __init__(self, width=80, height=80, nAnts=1000):
        """
        Initialize the model with width, height, and number of ants.
        """
        self.width = width
        self.height = height
        self.nAnts = nAnts

        # Our grid is a bunch of zero's in this case
        self.grid = np.zeros((height, width))

        # We initialize colony and food position with some padding included to make them not at the outer edges
        self.colony_position = (height - 5, width // 2)
        self.food_position = (4, width // 2)
        
        # Colony is -1 and food 1
        self.grid[self.colony_position] = -1
        self.grid[self.food_position] = 1

        # Initialize ants as a list of Ant objects
        self.ants = [Ant(*self.colony_position) for _ in range(nAnts)]

    def update(self):
        """
        Update the positions of all ants and stop if food is found.
        """
        food_found = False
        # For each ant we move it and check if it has found food.
        for ant in self.ants:
            ant.move(self.height, self.width)
            if tuple(ant.position) == self.food_position:
                food_found = True
        return food_found



class Ant:
    def __init__(self, x, y):
        """
        Class to model the ants. Each ant is initialized with a position.
        """
        self.position = [x, y]

    def valid_moves(self, height, width):
        """
        This function checks for valid moves, it iterates through each possible move range and returns the
        possible moves
        """
        moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:  # Exclude staying in the same position
                    new_x = self.position[0] + dx
                    new_y = self.position[1] + dy
                    # Check boundaries
                    if 0 <= new_x < height and 0 <= new_y < width:
                        moves.append((new_x, new_y))
        return moves
    
    def move(self, height, width):
        """
        Moves the ant one step in a random direction based on valid moves.
        """
        moves = self.valid_moves(height, width) 
        # Randomly select a move
        self.position = list(moves[np.random.randint(len(moves))])


class Visualization:
    def __init__(self, height, width, pauseTime=0.01):
        """
        This simple visualization shows the colony, food, and ants.
        """
        self.h = height
        self.w = width
        self.pauseTime = pauseTime
        grid = np.zeros((self.w, self.h))
        self.im = plt.imshow(grid, vmin=-1, vmax=2, cmap='rainbow')
        plt.title('Ant Simulation')

    def update(self, t, colony_position, food_position, ant_positions):
        """
        Updates the grid with colony, food, and ants for visualization.
        """
        grid = np.zeros((self.h, self.w))

        # Visualize the colony with a 3x3 radius in yellow (-1)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                x = (colony_position[0] + dx) % self.h
                y = (colony_position[1] + dy) % self.w
                grid[x, y] = -1

        # Visualize the food in green (1)
        grid[food_position[0], food_position[1]] = 1

        # Visualize the ants in black (2)
        for x, y in ant_positions:
            grid[x, y] = 2

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
    sim = Model()
    vis = Visualization(sim.height, sim.width)
    print('Starting simulation')
    while t < timeSteps:
        food_found = sim.update()  # Update simulation
        ant_positions = [ant.position for ant in sim.ants]
        vis.update(t, sim.colony_position, sim.food_position, ant_positions)
        if food_found:
            print(f"Food found at timestep {t}!")
            break
        t += 1
 #   vis.persist()
