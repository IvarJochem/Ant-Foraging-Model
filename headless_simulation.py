import numpy as np
import matplotlib.pyplot as plt
from maze_generator_with_nPaths import generate_maze_with_paths, upscale_maze

#test
class Model:
    def __init__(self, Maze, width, height, nAnts=1000, decay_rate = 0.95, pheromone_deposit=0.1, max_pheromone=0.9):
        """
        Initialize the model with width, height, and number of ants.
        """
        self.width = width
        self.height = height
        self.nAnts = nAnts
        self.decay = decay_rate
        # Our grid is a maze with walls (2) and open spaces (0)
        self.grid = Maze

        # We initialize colony in the center and the food at the top
        self.colony_position = (4, 4)
        self.food_position = (len(Maze[0])-6, len(Maze)-6)
        self.pheromone_deposit = pheromone_deposit
        self.max_pheromone = max_pheromone
        # Colony is represented as a -1 and food as a 1
        self.grid[self.colony_position] = -1
        self.grid[self.food_position] = 1
        #Initialize pheromone grid
        self.pheromones = np.zeros_like(Maze, dtype = float)
        # Initialize ants at the colony
        self.ants = [Ant(Maze, self.pheromones, self.colony_position[0], self.colony_position[1], pheromone_deposit, max_pheromone) for _ in range(nAnts)]

        # Track the food deliverd
        self.food_found = 0

        #Track the food discovered
        self.food_discovered = 0



    def update(self):
        """
        Update the positions of all ants and stop if food is found.
        """
        # Pheromone decay
        self.pheromones *= self.decay

        for ant in self.ants:
            ant.step(0.1)  # Update position and direction            
            # Check if ant has discovered food
            current_pos = (int(ant.position[0]), int(ant.position[1]))
            if not ant.hasfood and current_pos == self.food_position:
                self.food_discovered += 1
            
            # Check if ant has returned food to colony
            if ant.hasfood and current_pos == self.colony_position:
                self.food_found += 1
                ant.hasfood = False
                ant.visited = []
                ant.visited.append(ant.position)
                ant.path = []
                ant.path.append(ant.position)
                ant.time_since_last_update = 0.0


class Ant:
    def __init__(self, Maze, pheromones, x, y, pheromone_deposit, max_pheromone):
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
        self.pheromone_deposit = pheromone_deposit
        self.max_pheromone = max_pheromone
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
        adj_cells = [cell for cell in adj_cells if self.grid[int(cell[0]), int(cell[1])] != 2]
        # remove cells that are visited
        adj_cells = [cell for cell in adj_cells if cell not in self.visited]
        
        total_chance = 0
        for cell in adj_cells:
            total_chance += self.pheromones[int(cell[0]), int(cell[1])] + 0.1

        if total_chance == len(adj_cells)*0.1:
            #nothing happens, no pheromones
            np.random.shuffle(adj_cells)
            if len(adj_cells) == 0:
                return False
            else:
                return adj_cells[0]
        # pick a random number between 0 and the total pheromones
        pheromone_pick  = np.random.uniform(0, total_chance)
        current_chance = 0
        for cell in adj_cells:
            current_chance += self.pheromones[int(cell[0]), int(cell[1])] + 1
            if current_chance >= pheromone_pick:
                return cell

        
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
                    self.pheromones[x, y] = min(self.pheromones[x, y] +  self.pheromone_deposit , self.max_pheromone)
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
                cell = self.choose_cells_based_on_pheromones(adj_cells)
                if cell != False:
                    self.position = cell
                    self.visited.append(self.position)
                    self.path.append(self.position)
                    self.time_since_last_update = 0.0
                    return
          #  elif self.grid[int(self.position[0]), int(self.position[1])] >= 0 and self.grid[int(self.position[0]), int(self.position[1])] < 1:
        #        # Randomly emit pheromones for now
           #     self.grid[int(self.position[0]), int(self.position[1])] = np.random.uniform()
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

    def run(tempFileName='simulation_results',mazeCols=21, mazeRows=21, scaleFactor=3,  mazePaths=16, initialRandomseed=16436,
     Ants=1000, nStop=2500, foodFind=25, iterations=5, decay_rate = 0.9, pheromone_deposit=0.1, max_pheromone=0.9
    ):
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
            #Je kan de multiplicatie met randomseed weghalen als je steeds dezelfde seed wil checken.
            #Maze = generate_maze_with_paths(mazeCols, mazeRows, mazePaths, randomseed=initialRandomseed+i*152)
            Maze = generate_maze_with_paths(mazeCols, mazeRows, mazePaths, randomseed=initialRandomseed)
            Maze = upscale_maze(Maze, scaleFactor)
            sim = Model(Maze, len(Maze[0]), len(Maze), nAnts=Ants, decay_rate=0.9, pheromone_deposit=pheromone_deposit, max_pheromone=max_pheromone)
            # Heb hier schrijven we de initial settings
            filename = os.path.join(folder_name, f"{tempFileName}{i + 1}.txt")
            with open(filename, "w") as file:
                file.write(f"Simulation Iteration {i + 1}\n")
                file.write(f"Maze Dimensions: {mazeCols}x{mazeRows}, Scale Factor: {scaleFactor}, Paths: {mazePaths}\n")
                file.write(f"Number of Ants: {Ants}, Maximum Time Steps: {nStop}, Food Find Target: {foodFind}\n")
                file.write(f"Initial Random Seed: {initialRandomseed}\n")
                file.write(f"Pheromone decay rate: {decay_rate}, Deposit rate: {pheromone_deposit}, Max: {max_pheromone}")
                # this is the file for our baseline
                if pheromone_deposit==0:
                    file.write("Baseline: True\n")
                else:
                    file.write("Baseline: False")
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


    # Je kan de run functie gebruiken. Als je een parameter wil veranderen kan je of bovenin de functie de standaardwaardes veranderen,
    # of aangeven wat je wilt veranderen t.o.v. deze standaardwaardes zoals hieronder.
#    run(scaleFactor=2, iterations=2, initialRandomseed=1)

    # Je kan een for loop gebruiken om de naam te veranderen van de files waarin je het opslaat, hieronder een voorbeeld
    # van hoe je de decay zou kunnen simuleren.


    #hier heb ik de run functie aangepast om meerdere runs per maze te doen, en deze slaat ie op in hetzelfde txt file per maze
    #ik heb ook een parameter toegevoegd genaamd 'food discovered', dus wanneer ze het voedsel hebben gevonden
    def run(tempFileName='simulation_results', mazeCols=21, mazeRows=21, scaleFactor=3, mazePaths=5, 
        initialRandomseed=16436, Ants=1000, nStop=2500, foodFind=25, iterations=2, runs_per_maze=5):

        import os

        folder_name = "sim_results"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"Folder '{folder_name}' created.")
        else:
            print(f"Folder '{folder_name}' already exists.")

        for i in range(iterations):  # Outer loop: Create a new maze
            # Generate a unique maze for each iteration
            Maze = generate_maze_with_paths(mazeCols, mazeRows, mazePaths, randomseed=initialRandomseed + i * 152)
            Maze = upscale_maze(Maze, scaleFactor)

            # File for storing all runs for this maze
            filename = os.path.join(folder_name, f"{tempFileName}_maze{i + 1}.txt")
            with open(filename, "w") as file:
                file.write(f"Simulation for Maze {i + 1}\n")
                file.write(f"Maze Dimensions: {mazeCols}x{mazeRows}, Scale Factor: {scaleFactor}, Paths: {mazePaths}\n")
                file.write(f"Initial Random Seed for Maze: {initialRandomseed + i * 152}\n")
                file.write(f"Number of Ants: {Ants}, Maximum Time Steps: {nStop}, Food Find Target: {foodFind}\n")
                file.write("\nRun, Timestep, Food Found, AntsFood, Food Discovered\n")

                for run in range(runs_per_maze):  # Inner loop: Run the simulation multiple times for the same maze
                    print(f"Starting simulation for Maze {i + 1}, Run {run + 1}")
                    sim = Model(Maze, len(Maze[0]), len(Maze), nAnts=Ants)
                    t = 0
                    while t < nStop and not sim.food_found > foodFind - 1:
                        food_found = sim.update()  # Update simulation
                        file.write(f"{run + 1}, {t}, {sim.food_found}, {len([ant.hasfood for ant in sim.ants if ant.hasfood])}, {sim.food_discovered}\n")
                        t += 1

        print("Simulations complete.")

    run(scaleFactor=2, iterations=2, initialRandomseed=1, runs_per_maze=5)

