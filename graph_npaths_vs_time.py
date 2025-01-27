import numpy as np
import matplotlib.pyplot as plt
from maze_generator_with_nPaths import generate_maze_with_paths, upscale_maze
import ant_model_walkback as amw
from ant_model_walkback import Model, Ant
import random
import multiprocessing as mp
import time

# Set the parameters for the simulation
# Make sure to define the simulation parameters here or in run_process, as run_process won't have access to them otherwise
amw.ntimeSteps = 2500
amw.maze_dimention = 21
amw.maze_scale = 2
amw.ants_with_food_returned = 50
amw.nWaveAnts = 1

# List with times for each pheromone deposit rate
deposit_rates = [0, 0.1, 0.3, 0.5, 0.7, 0.9]
all_results = []

# Number of paths to test
nPaths_list = [16, 32, 55, 120]

# Number of iterations
iteration = 12

# Maze seeds
MAX_INT = 32**2 - 1
nMazes = 10
maze_seeds = [random.randint(0, MAX_INT) for i in range(nMazes)]

def run():
    start_time = time.time()
    for d_i, deposit_rate in enumerate(deposit_rates):
        print(f'Starting simulation with pheromone deposit rate: {deposit_rate}')
        print(f"{int(1/len(deposit_rates)*d_i*100)}% --- {time.time() - start_time} seconds ---")
        amw.pheromone_deposit = deposit_rate
        results = []
        # Different maze difficulties
        for nPaths in nPaths_list:
            # Shared array to store the times for each iteration
            shared_times = mp.Array('i', [-1] * iteration*nMazes)
            # List to store the processes
            processes = []
            for i in range(iteration*nMazes):
                # Create a new process for each iteration
                p = mp.Process(target=run_process, args=(nPaths, shared_times, i, i//iteration))
                processes.append(p)
                p.start()

            # Wait for all processes to finish
            for p in processes:
                p.join()

            # Count the number of simulations that ran out of time
            failed_count = 0
            for t in enumerate(shared_times):
                if t[1] == -1:
                    failed_count += 1
                    shared_times[t[0]] = amw.ntimeSteps

            # print(f'Timed out simulations: {failed_count}')

            avg_time = sum(shared_times) / len(shared_times)
            results.append((nPaths, avg_time))
    
        all_results.append((deposit_rate, results))

        #vis.persist()  # Keep the visualization open after the simulation

    # Plotting the results after all simulations
    plt.figure()
    for deposit_rate, results in all_results:
        if results:
            print(f"Time for deposit rate {deposit_rate}: {results}")
            # Extract x (number of paths) and y (time to find food) values
            x_values, y_values = zip(*results)
            
            #Plot results for this deposit rate 
            plt.plot(x_values, y_values, marker='o', linestyle='-', label = f"{deposit_rate}")

    # print the time it took to run the simulation
    print(f"100% --- {time.time() - start_time} seconds ---")
    # Plot the graph
    plt.xlabel('Number of paths')
    plt.ylabel('Foraging time')
    plt.title('Effect of maze difficulty on foraging time')
    plt.legend(title = 'Pheromone deposit rates')
    plt.show()

def run_process(nPaths, times, i, j):
    new_seed = maze_seeds[j]
    maze = generate_maze_with_paths(amw.maze_dimention, amw.maze_dimention, nPaths, randomseed=new_seed)
    maze = upscale_maze(maze, amw.maze_scale)
    # from ant_model_walkback import Model
    sim = Model(maze, len(maze[0]), len(maze))

    # Time of current iteration
    t = 0

    # Run the simulation for the current value of nPaths
    while t < amw.ntimeSteps:
        sim.update(t)  # Update simulation

        # Check if enough ants have returned with food
        if sim.food_found > amw.ants_with_food_returned - 1:
            times[i] = t
            return

        t += 1


if __name__ == '__main__':
    """
    Simulation parameters
    """
    run()


