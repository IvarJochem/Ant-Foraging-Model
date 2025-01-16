import numpy as np
import matplotlib.pyplot as plt
from maze_generator_with_nPaths import generate_maze_with_paths
from mazegenerator import upscale_maze

#test
class Model:
    def __init__(self, Maze, width, height, nAnts=1000):
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
        #Initialize pheromone grid
        self.pheromones = np.zeros_like(Maze, dtype = float)
        # Initialize ants at the colony
        self.ants = [Ant(Maze, self.pheromones, self.colony_position[0], self.colony_position[1]) for _ in range(nAnts)]

        # Track the food deliverd
        self.food_found = 0



    def update(self):
        """
        Update the positions of all ants and stop if food is found.
        """
        # Pheromone decay of 1%
        self.pheromones *= 0.99
        for ant in self.ants:
            ant.step(0.1)  # Update position and direction
            # Check if an ant has found the food
            if ant.hasfood and (int(ant.position[0]), int(ant.position[1])) == self.colony_position:
                self.food_found += 1  # Increment the food delivered count
                ant.hasfood = False
                ant.visited = []
                ant.visited.append(ant.position)
                ant.path = []
                ant.path.append(ant.position)
                ant.time_since_last_update = 0.0
        # Pheromone decay of 10%
        self.pheromones *= 0.90



class Ant:
    def __init__(self, Maze, pheromones, x, y):
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
        self.hasfood = False
        self.pheromones = pheromones

    def get_adjacent_cells(self):
        """
        Get the adjacent cells of the ant in the grid.
        """
        x, y = self.position
        adj_cells = [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
        return adj_cells

    def shuffle_cells_with_bias(self, adj_cells, bias=0):
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
            # check if the ant has food
            if self.grid[int(self.position[0]), int(self.position[1])] == 1:
                self.hasfood = True
            if self.hasfood:
                x, y = int(self.position[0]), int(self.position[1])
                if self.grid[x, y] >= 0 and self.grid[x, y] < 1:
                    self.pheromones[x, y] = min(self.pheromones[x, y] + 0.1, 0.9)
            # check if the ant is at the colony and has food
            if self.hasfood and self.position == self.colony_position:
                self.hasfood = False
                self.visited = []
                self.visited.append(self.position)
                self.path = []
                self.path.append(self.position)
                self.time_since_last_update = 0.0
                return

            if not self.hasfood:
                # check adjacent cells for cells that the ant has not visited
                # and move to the cell that has not been visited
                adj_cells = self.get_adjacent_cells()
                # shuffle the adjacent cells to randomize the movement
                adj_cells = self.shuffle_cells_with_bias(adj_cells)
                for cell in adj_cells:
                    if self.grid[int(cell[0]), int(cell[1])] != 2 and cell not in self.visited:
                        self.position = cell
                        self.visited.append(self.position)
                        self.path.append(self.position)
                        self.time_since_last_update = 0.0
                        return

            # move back to the colony along the path
            self.position = self.path[-2]
            self.path.pop()
            # print(f"Backtracking to {self.position}")
            self.time_since_last_update = 0.0
            return



if __name__ == '__main__':
    """
    Simulation parameters
    """
    def run(tempFileName='simulation_results',mazeCols=21, mazeRows=21, scaleFactor=3,  mazePaths=16, initialRandomseed=16436, Ants=1000, nStop=2500, foodFind=25, iterations=5):
        import os
        folder_name = "sim_results"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"Folder '{folder_name}' created.")
        else:
            print(f"Folder '{folder_name}' already exists.")


        for i in range(iterations):
            timeSteps = nStop
            t = 0
            # add i to vary the seed
            Maze = generate_maze_with_paths(mazeCols, mazeRows, mazePaths, randomseed=initialRandomseed+i*152)
            Maze = upscale_maze(Maze, scaleFactor)
            sim = Model(Maze, len(Maze[0]), len(Maze), nAnts=Ants)
            # Heb hier schrijven we de initial settings
            filename = os.path.join(folder_name, f"{tempFileName}{i + 1}.txt")
            with open(filename, "w") as file:
                file.write(f"Simulation Iteration {i + 1}\n")
                file.write(f"Maze Dimensions: {mazeCols}x{mazeRows}, Scale Factor: {scaleFactor}, Paths: {mazePaths}\n")
                file.write(f"Number of Ants: {Ants}, Maximum Time Steps: {nStop}, Food Find Target: {foodFind}\n")
                file.write(f"Initial Random Seed: {initialRandomseed + i * 152}\n")
                # this is the file for our baseline
                file.write("Baseline: True\n")
                file.write("Starting simulation\n\n")
                file.write("Timestep, Food Found, AntsFood\n")
                print('Starting simulation')
                n = foodFind
                while t < timeSteps and not sim.food_found > n-1:
                    food_found = sim.update()  # Update simulation
                    # Je kan dingen van de model writen met sim. zoals bij sim.food_found
                    # en dingen van de mieren via het callen van sim.ants, hierna kan je met ant.hasfood bijvoorbeeld
                    # een lijst maken van elk geval waneer een mier eten draagt. Laatste parameter houdt dus bij hoeveel
                    # mieren eten dragen.
                    file.write(f"{t}, {sim.food_found}, {len([ant.hasfood for ant in sim.ants if ant.hasfood])}\n")

                    t += 1

    # Je kan in run aangeven wat je wilt aanpassen t.o.v. van de baseline. Is normaal de bedoeling dat je 1 parameter tegelijk aanpast
    # maar nu weten we nog niet precies wat we allemaal willen.
    # Dit was gemaakt in een versie waar pheromonen nog niet werkte. Ik kan later nog wel kijken naar een optie
    # om pheromonen uit en aan te zetten, en dan de simulatie te runnen in dezelfde maze met en zonder pheromonen.
    # Voor nu is dit denk het wel genoeg om alvast aan wat visualisaties te werken van hoe snel een mier nou precies x aantal eten vindt.
    # Dan kunnen we later die code hergebruiken om te zien wat het verschil is als pheromonen wel een rol spelen.
    run(scaleFactor=2, iterations=2, initialRandomseed=1)

    # Als je meerdere keren dezelfde maze wilt runnen kan je iets zoals dit doen om het in meerdere txts bestand op te slaan. Die i is 
    # ervoor dat je niet telkens dezelfde bestanden overwrite
    # Voor het inlezen van het bestand moet je een paar rows overslaan, daarna kan je het met pandas ofzo het in zo'n dataframe zetten
    # voor makkelijke visualisatie. Of natuurlijk iets anders, maakt niet heel veel uit.
    """
    for i in range(10):
        filenametosave = str(i)+'tempFileName'
        run(tempFileName= filenametosave)
    
    """