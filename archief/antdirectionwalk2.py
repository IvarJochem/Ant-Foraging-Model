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

        # Our grid is a bunch of zeros
        self.grid = np.zeros((height, width))


        # We initialize colony in the center and the food at the top
        self.colony_position = (height // 2, width // 2)
        self.food_position = (4, width // 2)

        # Colony is represented as a -1 and food as a 1
        self.grid[self.colony_position] = -1
        self.grid[self.food_position] = 1

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
            ant.step(0.1)  # Update position and direction
            # Check if an ant has found the food
            if (int(ant.position[0]), int(ant.position[1])) == self.food_position:
                food_found = True
        return food_found


class Ant:
    def __init__(self, x, y, direction, move_speed=1, direction_update_period=0.25, noise_range=np.pi * 0.02):
        """
        Class to model the ants. Each ant is initialized with a position and direction.
        """
        self.position = np.array([x, y], dtype=np.float32)
        self.angle = direction
        self.move_speed = move_speed
        self.direction_update_period = direction_update_period
        self.noise_range = noise_range
        self.time_since_last_update = 0.0
        self.has_moved_away = False

    def update_direction(self):
        """Update the ant's direction with some randomness."""
        noise = np.random.uniform(-self.noise_range, self.noise_range)
        self.angle += noise

    def move(self, dt):
        """Move the ant in its current direction with faster movement."""
        direction = np.array([np.cos(self.angle), np.sin(self.angle)])
        speed_multiplier = 1.5  # Factor to make ants move faster
        self.position += direction * self.move_speed * speed_multiplier * dt

    def step(self, dt):
        """Update the ant's state for the given time step."""
        # If the ant hasn't moved away from the colony yet, move in the direction away from the colony
        if not self.has_moved_away:
            # Vector pointing from the colony to the ant's current position
            direction_to_colony = np.array([self.position[0] - 40, self.position[1] - 40])
            direction_to_colony /= np.linalg.norm(direction_to_colony)
            self.angle = np.arctan2(direction_to_colony[1], direction_to_colony[0])  # Point directly away from the colony
            self.position += direction_to_colony * self.move_speed * dt  # Move away from the colony
            self.has_moved_away = True  # Mark as having moved away from the colony
        else:
            # Once the ant has moved away, update its direction with some noise and move as usual
            self.time_since_last_update += dt
            if self.time_since_last_update >= self.direction_update_period:
                self.update_direction()
                self.time_since_last_update = 0.0
            self.move(dt)


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
