import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Ant:
    def __init__(self, position, angle, move_speed=4.0, direction_update_period=0.25, noise_range=np.pi * 0.02):
        self.position = np.array(position, dtype=np.float32)
        self.angle = angle
        self.move_speed = move_speed
        self.direction_update_period = direction_update_period
        self.noise_range = noise_range
        self.time_since_last_update = 0.0

    def update_direction(self):
        """Update the ant's direction with some randomness."""
        noise = np.random.uniform(-self.noise_range, self.noise_range)
        self.angle += noise

    def move(self, dt):
        """Move the ant in its current direction."""
        direction = np.array([np.cos(self.angle), np.sin(self.angle)])
        self.position += direction * self.move_speed * dt

    def step(self, dt):
        """Update the ant's state for the given time step."""
        self.time_since_last_update += dt
        if self.time_since_last_update >= self.direction_update_period:
            self.update_direction()
            self.time_since_last_update = 0.0
        self.move(dt)

class AntSimulation:
    def __init__(self, num_ants, world_size):
        self.ants = [Ant(
            position=(np.random.uniform(0, world_size[0]), np.random.uniform(0, world_size[1])),
            angle=np.random.uniform(0, 2 * np.pi)
        ) for _ in range(num_ants)]
        self.world_size = world_size
        self.fig, self.ax = plt.subplots()
        self.scatter = self.ax.scatter([], [], s=10, c='blue')

    def update(self, frame):
        """Update function for the animation."""
        dt = 0.1
        positions = []
        for ant in self.ants:
            ant.step(dt)
            # Keep ants within bounds
            ant.position[0] %= self.world_size[0]
            ant.position[1] %= self.world_size[1]
            positions.append(ant.position)

        positions = np.array(positions)
        self.scatter.set_offsets(positions)
        return self.scatter,

    def run(self):
        """Run the simulation."""
        self.ax.set_xlim(0, self.world_size[0])
        self.ax.set_ylim(0, self.world_size[1])
        self.ani = animation.FuncAnimation(
            self.fig, self.update, frames=200, interval=50, blit=True
        )
        plt.show()

# Parameters
num_ants = 50
world_size = (100, 100)

# Run the simulation
simulation = AntSimulation(num_ants, world_size)
simulation.run()
