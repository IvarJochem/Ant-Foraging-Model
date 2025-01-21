import pandas as pd
import matplotlib.pyplot as plt
import os


###########
#### the following functions are for when checking 1 txt file and plotting a variable over time
#### so in the current situation, this means that the in 1 txt file, the simulation of the same maze is saved multiple different times
###########

# Function to load and split data by run from the text file
def load_data(file_path, column_names):
    """
    Load and split simulation data by run from the text file.
    """
    # Read the entire file into a DataFrame
    data = pd.read_csv(file_path, skiprows=8, names=column_names)

    # Split the data by run (group by "Run")
    runs = []
    for run_number, run_data in data.groupby("Run"):
        runs.append(run_data.drop("Run", axis=1))  # Drop the "Run" column for clarity
    return runs

# Plot variable Over Time
def plot_variable(data, run_number, variable):
    """
    Plot Food Found Over Time for each run.
    """

    plt.plot(data["Timestep"], data[variable], label=f"Run {run_number}", linewidth=2)
    plt.xlabel("Timestep")
    plt.ylabel(variable)
    plt.title(f"{variable} Over Time")


def average_timestep_variable_first_happening(file_path, x_food, variable_firsth_happening, column_names):
    """
    Calculate the average timestep when x_value amount of the specified column is found 
    in all runs within a single txt file.
    """
    # Load the data for the file (multiple runs)
    runs = load_data(file_path, column_names)
    
    # List to store the first timestep where x_value or more of the specified column is found for each run
    timesteps = []

    # Iterate over all runs
    for run_data in runs:
        # Find the first timestep where x_value or more of the specified column is found
        first_x_value_timestep = run_data.loc[run_data[variable_firsth_happening] >= x_food, "Timestep"].min()

        # If such a timestep exists, append it to the timesteps list
        if pd.notna(first_x_value_timestep):
            timesteps.append(first_x_value_timestep)
    
    # Calculate the average timestep
    if timesteps:
        average_timestep = sum(timesteps) / len(timesteps)
    else:
        print(f"No run found {x_food} or more of {variable_firsth_happening}.")
        return None  # Return None if no such timestep is found

    return average_timestep


# Results for one simulation file of the same maze with multiple runs)
def results_one_txt_file(file_path, x_food, variable_first_timestep_happening, column_names):
    """
    Show the results for 1 txt file with multiple runs.
    """
    # Load the data for 1 txt file with multiple runs
    runs = load_data(file_path, column_names)

    # figure for variable over time
    plt.figure(figsize=(10, 6))
    # Generate plots for each run in the txt file
    for i, run_data in enumerate(runs, 1):
        plot_variable(data=run_data, run_number=i, variable=variable)
    plt.legend()
    plt.grid()


    # Find the average first timestep where x_food or more was found or discovered or something else, depending on the variable given
    first_x = average_timestep_variable_first_happening(file_path=file_path, x_food=x_food, variable_firsth_happening=variable_first_timestep_happening ,column_names=column_names, )

    # Add a text box showing the first timestep where x_food was found or discovered or something else, depending on the variable given
    if pd.notna(first_x):
        textstr = f"First {x_food} {variable}:\nTimestep {first_x} (average)"
    else:
        textstr = f"{x_food} Food Not Found"
    
    plt.gcf().text(
        0.7, 0.75, textstr, fontsize=10, color="black", bbox=dict(facecolor="white", edgecolor="green", boxstyle="round,pad=0.5")
    )

    plt.show()




###########
#### the following functions are for when checking 1 folder and plotting a variable over time, so multiple txt files in that folder
#### so in the current situation, this means that the in folder txt file, there are multiple txt files of each a maze with the same conditions but randomly made for each iteration, and multiple runs per maze
###########

# Function to load all simulation result files from a folder
def load_simulation_files(folder_path, column_names):
    """
    Load all simulation result files from a folder into a list of DataFrames, split by runs.
    """
    data_frames = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt"):
            file_path = os.path.join(folder_path, file_name)
            runs = load_data(file_path, column_names=column_names)  # Load and split by run
            data_frames.append(runs)
    return data_frames


# Plot all simulation results from all runs in one graph
def plot_all_simulations(data_frames, variable):
    """
    Plot all simulation results in one graph.
    """
    plt.figure(figsize=(10, 6))
    for runs in data_frames:
        for i, run_data in enumerate(runs, 1):
            plt.plot(run_data["Timestep"], run_data[variable], label=f"Run {i}", alpha=0.7)
    plt.xlabel("Timestep")
    plt.ylabel(variable)
    plt.title(f"{variable} Over Time (All Runs)")
    plt.legend()
    plt.grid()
    plt.show()

# Plot the average simulation over all runs
def plot_average_simulation(data_frames, variable):
    """
    Compute and plot the average of all simulations across all runs.
    """
    all_data = []
    for runs in data_frames:
        for run_data in runs:
            all_data.append(run_data)

    # Combine data and calculate mean for each timestep
    combined_data = pd.concat(all_data).groupby("Timestep").mean()

    plt.figure(figsize=(10, 6))
    plt.plot(combined_data.index, combined_data[variable], label=variable, color="green", linewidth=2)
    plt.xlabel("Timestep")
    plt.ylabel(variable)
    plt.title(f"average {variable} Over Time of all simulations and mazes (with the same conditions)")
    plt.legend()
    plt.grid()
    plt.show()

def results_simulation_with_multiple_random_mazes(folder_path, variable, column_names):
    
    data_frames = load_simulation_files(folder_path, column_names=column_names)

    # Visualization options
    plot_all_simulations(data_frames, variable)        # Plot all runs
    plot_average_simulation(data_frames, variable)     # Plot average over all runs



if __name__ == "__main__":

    column_names = ["Run", "Timestep", "FoodFound", "AntsFood", "FoodDiscovered"]

    #change this to the variable you want to visualize
    variable = "FoodDiscovered"


    # Results for 1 txt file (with multiple runs)
    file_path = "/Users/anthonyhessing/sim_results/simulation_results_maze1.txt" #edit this so it works, did this locally on my laptop
    results_one_txt_file(file_path=file_path, x_food=1, variable_first_timestep_happening=variable, column_names=column_names)
  
    # Folder containing simulation result files (multiple txt files with multiple runs)
    folder_path = "/Users/anthonyhessing/sim_results"
    results_simulation_with_multiple_random_mazes(folder_path=folder_path, variable=variable, column_names=column_names)


