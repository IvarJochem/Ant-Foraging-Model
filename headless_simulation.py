import numpy as np
import matplotlib.pyplot as plt
from maze_generator_with_nPaths import generate_maze_with_paths, upscale_maze
import ant_model_walkback as amw
from ant_model_walkback import Model, Ant


if __name__ == '__main__':
    """
    Simulation parameters
    """
    amw.nPaths = 16
    amw.maze_dimention = 21
    amw.maze_scale = 3
    amw.nAnts = 1000
    amw.nWaveAnts = 100
    amw.WaveTimesteps = 100
    amw.colony_position = (amw.maze_scale, amw.maze_scale)
    amw.food_position = (amw.maze_size-amw.maze_scale-1, amw.maze_size-amw.maze_scale-1)
    amw.ants_with_food_returned = 25
    amw.pheromone_deposit = 0.1
    amw.decay_rate = 0.9
    amw.max_pheromone = 0.99

    def run(tempFileName='simulation_results', initialRandomseed=16436, nStop=2500, iterations=5):
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
            Maze = generate_maze_with_paths(amw.maze_dimention, amw.maze_dimention, amw.nPaths, randomseed=initialRandomseed)
            Maze = upscale_maze(Maze, amw.maze_scale)
            sim = Model(Maze, len(Maze[0]), len(Maze))
            # Heb hier schrijven we de initial settings
            filename = os.path.join(folder_name, f"{tempFileName}{i + 1}.txt")
            with open(filename, "w") as file:
                file.write(f"Simulation Iteration {i + 1}\n")
                file.write(f"Maze Dimensions: {amw.maze_dimention}x{amw.maze_dimention}, Scale Factor: {amw.maze_scale}, Paths: {amw.nPaths}\n")
                file.write(f"Number of Ants: {amw.nAnts}, Maximum Time Steps: {nStop}, Food Find Target: {amw.ants_with_food_returned}\n")
                file.write(f"Initial Random Seed: {initialRandomseed}\n")
                file.write(f"Pheromone decay rate: {amw.decay_rate}, Deposit rate: {amw.pheromone_deposit}, Max: {amw.max_pheromone}")
                # this is the file for our baseline
                if amw.pheromone_deposit==0:
                    file.write("Baseline: True\n")
                else:
                    file.write("Baseline: False")
                file.write("Starting simulation\n\n")
                file.write("Timestep, Food Found, AntsFood\n")
                print('Starting simulation')
                n = amw.ants_with_food_returned
                while t < timeSteps and not sim.food_found > n-1:
                    amw.ants_with_food_returned = sim.update(t)  # Update simulation
                    # Je kan dingen van de model writen met sim. zoals bij sim.food_found
                    # en dingen van de mieren via het callen van sim.ants, hierna kan je met ant.hasfood bijvoorbeeld
                    # een lijst maken van elk geval waneer een mier eten draagt. Laatste parameter houdt dus bij hoeveel
                    # mieren eten dragen.
                    file.write(f"{t}, {sim.food_found}, {len([Ant.hasfood for ant in sim.ants if Ant.hasfood])}\n")

                    t += 1


    # Je kan de run functie gebruiken. Als je een parameter wil veranderen kan je of bovenin de functie de standaardwaardes veranderen,
    # of aangeven wat je wilt veranderen t.o.v. deze standaardwaardes zoals hieronder.
    run(scaleFactor=2, iterations=2, initialRandomseed=1)

    # Je kan een for loop gebruiken om de naam te veranderen van de files waarin je het opslaat, hieronder een voorbeeld
    # van hoe je de decay zou kunnen simuleren.


