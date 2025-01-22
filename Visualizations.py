import pandas as pd
import matplotlib.pyplot as plt
import os


# Function to load and split data by run from the text file
def load_data(file_path, column_names):
    """
    Load and split simulation data by run from the text file.
    """
    data = pd.read_csv(file_path, skiprows=7, names=column_names)
    return data


def plot_average_food_found_one_folder(folder_path, column_names):
    """
    Load multiple files from a folder, calculate the average Food Found for each timestep, 
    and plot the results.
    """
    all_data = []

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        
        if os.path.isfile(file_path) and file_name.endswith('.txt'):
            data = pd.read_csv(file_path, skiprows=7, names=column_names)
            all_data.append(data)
    
    if not all_data:
        print("No valid files found in the folder.")
        return
    
    combined_data = pd.concat(all_data, axis=0)
    
    # Group by Timestep and calculate the average Food Found
    average_data = combined_data.groupby("Timestep").mean().reset_index()
    
    plt.figure(figsize=(10, 6))
    plt.plot(average_data["Timestep"], average_data["Food Found"], label="Average Food Found", color='blue', marker='o')
    plt.xlabel("Timestep")
    plt.ylabel("Food Found")
    plt.title("Average Food Found Over Time")
    plt.grid(True)
    plt.legend()
    plt.show()

def plot_average_food_found_multiple_folders(main_folder, sub_folders, column_names):
    """
    Load multiple files from multiple folders, calculate the average Food Found for each timestep
    per folder, and plot all results in one graph with different lines.
    """

    plt.figure(figsize=(10, 6))
    
    colors = ['blue', 'red', 'green', 'purple', 'orange', 'brown', 'pink', 'gray', 'yellow', 'black']
    
    for folder_idx, folder_path in enumerate(sub_folders):
        all_data = []
        
        # Get all files from current folder
        sub_folder_path = os.path.join(main_folder, folder_path)
        
        for file_name in os.listdir(sub_folder_path):
            file_path = os.path.join(sub_folder_path, file_name)
            
            if os.path.isfile(file_path) and file_name.endswith('.txt'):
                data = pd.read_csv(file_path, skiprows=7, names=column_names)
                all_data.append(data)
        
        if not all_data:
            print(f"No valid files found in folder: {folder_path}")
            continue
        
        # Combine all data from this folder
        combined_data = pd.concat(all_data, axis=0)
        
        # Calculate average for this folder
        average_data = combined_data.groupby("Timestep").mean().reset_index()
        
        # Folder name for legend
        folder_name = os.path.basename(folder_path)
        
        # Plot with different color for each folder
        color = colors[folder_idx % len(colors)]  
        plt.plot(average_data["Timestep"], 
                average_data["Food Found"], 
                label=f"{folder_name}",
                color=color,
                marker='o',
                markersize=2)
    
    plt.xlabel("Timestep")
    plt.ylabel("Food Found")
    plt.title("Average Food Found Over Time - Multiple Runs")
    plt.grid(True)
    plt.legend()
    plt.show()

# Main execution
def main():
    folder_path = "sim_results/decay_0.7"  
    column_names = ["Timestep", "Food Found", "AntsFood"]
    plot_average_food_found_one_folder(folder_path, column_names)

    main_folder = "sim_results"
    sub_folders = ["decay_0.9999", "decay_0.9", "decay_0.8", "decay_0.7", "decay_0.6", "decay_0.5", "decay_0.4", "decay_0.3", "decay_0.2", "decay_0.1", "decay_0.0"]
    column_names = ["Timestep", "Food Found", "AntsFood"]
    plot_average_food_found_multiple_folders(main_folder, sub_folders, column_names)


if __name__ == "__main__":
    main()





