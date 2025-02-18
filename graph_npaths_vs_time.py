import matplotlib.pyplot as plt
from maze_generator_with_nPaths import generate_maze_with_paths, upscale_maze
import ant_model_walkback as amw
from ant_model_walkback import Model
import random
import multiprocessing as mp
import time
from scipy.stats import f_oneway

# Set the parameters for the simulation
# Make sure to define the simulation parameters here or in run_process,
# as run_process won't have access to them otherwise
amw.ntimeSteps = 2500
amw.maze_dimention = 31
amw.maze_scale = 1
amw.ants_with_food_returned = 500
amw.nWaveAnts = 1
amw.decay_rate = 0.2

# List with times for each pheromone deposit rate
deposit_rates = [0, 0.5]
all_results = []

# Number of paths to test
nPaths_list = [16, 32, 55, 120]

# Number of iterations
iteration = 7

# Maze seeds
MAX_INT = 32**2 - 1
nMazes = 10
maze_seeds = [random.randint(0, MAX_INT) for i in range(nMazes)]

def run():
    start_time = time.time()

    # Collect results for boxplots
    boxplot_data = {0: {nPaths: [] for nPaths in nPaths_list}, 0.5: {nPaths: [] for nPaths in nPaths_list}}

    # Colors for boxplots
    deposit_colors = {0: "lightpink", 0.5: "lightgreen"}

    for d_i, deposit_rate in enumerate(deposit_rates):
        # Only plot deposit rates 0 and 0.5
        if deposit_rate not in [0, 0.5]:
            continue
        print(f'Starting simulation with pheromone deposit rate: {deposit_rate}')
        print(f"{int(1/len(deposit_rates)*d_i*100)}% --- {time.time() - start_time} seconds ---")
        amw.pheromone_deposit = deposit_rate

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

            # Add times for current difficulty and deposit rate to boxplot
            boxplot_data[deposit_rate][nPaths].extend(shared_times)

    # ANOVA test for statistical analysis
    for deposit_rate in [0, 0.5]:
        data_groups = [boxplot_data[deposit_rate][nPaths] for nPaths in nPaths_list]
        stat, p_value = f_oneway(*data_groups)
        print(f"ANOVA for deposit rate {deposit_rate}: F={stat:.3f}, p={p_value:.3g}")

    # Plotting the results after all simulations
    plt.figure()
    for d_i, (deposit_rate, color) in enumerate(deposit_colors.items()):
        data = [boxplot_data[deposit_rate][nPaths] for nPaths in nPaths_list]
        positions = [x + (d_i * 0.3) for x in range(len(nPaths_list))]  # Offset for each deposit rate
        plt.boxplot(data, positions=positions, widths=0.25, patch_artist=True,
                    boxprops=dict(facecolor=color),
                    medianprops=dict(color='black'),
                    labels=[str(n) for n in nPaths_list] if d_i == 0 else None)

    # print the time it took to run the simulation
    print(f"100% --- {time.time() - start_time} seconds ---")
    # Plot the graph
    plt.xticks(ticks=range(len(nPaths_list)), labels=nPaths_list)
    plt.xlabel('Number of paths')
    plt.ylabel('Foraging time')
    plt.title('Effect of maze difficulty on foraging time')
    legend_labels = [f"Pheromone deposit = {rate}" for rate in deposit_colors.keys()]
    legend_colors = [plt.Line2D([0], [0], color=color, lw=4) for color in deposit_colors.values()]
    plt.legend(legend_colors, legend_labels, title='Deposit rates')
    plt.show()

def run_process(nPaths, times, i, j):
    new_seed = maze_seeds[j]
    maze = generate_maze_with_paths(amw.maze_dimention, amw.maze_dimention, nPaths, randomseed=new_seed)
    maze = upscale_maze(maze, amw.maze_scale)
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
