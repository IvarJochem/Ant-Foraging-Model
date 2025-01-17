import numpy as np
import matplotlib.pyplot as plt

class Model:
    def __init__(self, width=80, height=80, nAnts=100):
        """
        Initialize the model with width, height, and number of ants.
        """
        self.width = width
        self.height = height
        self.nAnts = nAnts

        # Define the grid
        self.grid = np.zeros((height, width))

        # Initialize positions for the colony and the food
        self.colony_position = (height // 2, width // 2)  # Center of the grid
        self.food_position = (4, width // 2)  # Near top center with padding

        # Place colony and food on the grid
        self.grid[self.colony_position] = -1  # Colony represented by -1
        self.grid[self.food_position] = 1  # Food represented by 1

        # Initialize ants in a circle around the colony
        radius = 5
        angles = np.linspace(0, 2 * np.pi, nAnts, endpoint=False)
        self.ants = [
            Ant(
                self.colony_position[0] + radius * np.sin(angle),
                self.colony_position[1] + radius * np.cos(angle),
                angle
            )
            for angle in angles
        ]

    def update(self):
        """
        Update the positions of all ants and stop if food is found.
        """
        food_found = False
        for ant in self.ants:
            ant.move(self.height, self.width)
            # Check if an ant has found the food
            if (int(ant.position[0]), int(ant.position[1])) == self.food_position:
                food_found = True
        return food_found


class Ant:
    def __init__(self, x, y, direction):
        """
        Class to model the ants. Each ant is initialized with a position and direction.
        """
        self.position = np.array([x, y], dtype=np.float32)
        self.direction = direction  # Angle in radians
        self.speed = 0.5  # Movement speed

    def move(self, height, width):
        """
        Moves the ant in a smooth random wandering pattern.
        """
        # Update position based on current direction and speed
        self.position += self.speed * np.array([
            np.sin(self.direction),
            np.cos(self.direction)
        ])

        # Add small random noise to the direction for wandering behavior
        self.direction += np.random.uniform(-0.1, 0.1)

        # Enforce periodic boundary conditions
        self.position[0] %= height
        self.position[1] %= width


class Visualization:
    def __init__(self, height, width, pauseTime=0.1):
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
            grid[int(x), int(y)] = 2

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
   # vis.persist()
