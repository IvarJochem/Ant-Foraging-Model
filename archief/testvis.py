import os
import numpy as np
import matplotlib.pyplot as plt

# Path to the directory containing the files
sim_results_dir = ["sim_results", "sim_results2", "sim_results3"]
decay_values = [0.9, 0.95, 0.99]
# Function to process files and compute averages
def process_files(sim_results):
    timestep_data = {}  # To store timestep averages

    # Iterate through prefixes from 0 to 9
    for prefix in range(10):
        food_found_accumulator = {}
        count_per_timestep = {}

        # Process files from 0tempFileName1.txt to 0tempFileName5.txt, 1tempFileName1.txt to 1tempFileName5.txt, etc.
        for file_suffix in range(1, 6):
            filename = os.path.join(sim_results, f"{prefix}tempFileName{file_suffix}.txt")

            # Check if file exists
            if not os.path.isfile(filename):
                print(f"File not found: {filename}")
                continue

            with open(filename, "r") as file:
                lines = file.readlines()

                # Skip the first 7 lines
                data_lines = lines[8:]

                # Process each line after the header
                for line in data_lines:
                    parts = line.strip().split(",")
                    if len(parts) != 3:
                        continue

                    try:
                        timestep = int(parts[0])
                        food_found = float(parts[1])

                        # Accumulate food found for each timestep
                        if timestep not in food_found_accumulator:
                            food_found_accumulator[timestep] = 0
                            count_per_timestep[timestep] = 0

                        food_found_accumulator[timestep] += food_found
                        count_per_timestep[timestep] += 1

                    except ValueError:
                        print(f"Invalid data in file {filename}: {line}")

        # Compute averages for this prefix
        averages = {timestep: food_found_accumulator[timestep] / count_per_timestep[timestep]
                    for timestep in food_found_accumulator}

        # Store averages for plotting
        timestep_data[prefix] = averages

    return timestep_data
# Plotting function
def plot_data(timestep_data_list, labels):
    num_dirs = len(timestep_data_list)
    fig, axes = plt.subplots(1, num_dirs, figsize=(15, 6), sharey=True)

    if num_dirs == 1:
        axes = [axes]  # Ensure axes is iterable for a single subplot

    for ax, timestep_data, decay_value in zip(axes, timestep_data_list, labels):
        for prefix, averages in timestep_data.items():
            timesteps = sorted(averages.keys())
            avg_food = [averages[t] for t in timesteps]

            decay_value = prefix * 0.01  # Calculate decay value
            ax.plot(timesteps, avg_food, label=f"pheromone deposit={decay_value:.2f}")
        ax.set_title(f"decay={decay_value}")
        ax.set_xlabel("Timestep")
        ax.set_ylabel("Average Food Found")
        ax.legend()
        ax.grid(True)

    plt.tight_layout()
    plt.show()

# Main execution
def main():
    timestep_data_list = []
    labels = []

    for sim_results in sim_results_dir:
        timestep_data = process_files(sim_results)
        timestep_data_list.append(timestep_data)
        labels.append(os.path.basename(sim_results))

    plot_data(timestep_data_list, labels)

if __name__ == "__main__":
    main()
