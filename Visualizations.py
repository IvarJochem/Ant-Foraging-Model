import pandas as pd
import matplotlib.pyplot as plt
import os


def find_header_index(file_path):
    with open(file_path, 'r') as file:
        for i, line in enumerate(file):
            if 'Timestep, Food Found, AntsFood' in line:
                return i + 1
    return 0

def plot_average_food_found_one_folder(folder_path, path_where_to_save_graph, graph_name):
    """
    Load multiple files from a folder, calculate the average Food Found for each timestep, 
    and plot the results.
    """
    all_data = []
    column_names = ["Timestep", "Food Found", "AntsFood"]

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        
        if os.path.isfile(file_path) and file_name.endswith('.txt'):
            skiprows = find_header_index(file_path=file_path)
            data = pd.read_csv(file_path, skiprows=skiprows, names=column_names)
            all_data.append(data)
    
    if not all_data:
        print("No valid files found in the folder.")
        return
    
    combined_data = pd.concat(all_data, axis=0)
    
    # Group by Timestep and calculate the average Food Found
    average_data = combined_data.groupby("Timestep").mean().reset_index()
    
    plt.figure(figsize=(10, 6))
    plt.plot(average_data["Timestep"], average_data["Food Found"], label="Average Food Found", color='blue', marker='o', markersize=1)
    plt.xlabel("Timestep")
    plt.ylabel("Food Found")
    plt.title("Average Food Found Over Time")
    plt.grid(True)
    plt.legend()

    full_path = os.path.join(path_where_to_save_graph, graph_name)
    plt.savefig(full_path)
    plt.close()

def plot_average_food_found_multiple_folders(main_folder, sub_folders, path_where_to_save_graph, graph_name):
    """
    Load multiple files from multiple folders, calculate the average Food Found for each timestep
    per folder, and plot all results in one graph with different lines.
    """

    column_names = ["Timestep", "Food Found", "AntsFood"]

    plt.figure(figsize=(10, 6))
    
    colors = ['blue', 'red', 'green', 'purple', 'orange', 'brown', 'pink', 'gray', 'yellow', 'black']
    
    for folder_idx, folder_path in enumerate(sub_folders):
        all_data = []
        
        # Get all files from current folder
        sub_folder_path = os.path.join(main_folder, folder_path)
        
        for file_name in os.listdir(sub_folder_path):
            file_path = os.path.join(sub_folder_path, file_name)
            
            if os.path.isfile(file_path) and file_name.endswith('.txt'):
                skiprows = find_header_index(file_path=file_path)
                data = pd.read_csv(file_path, skiprows=skiprows, names=column_names)
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

        folder_name = os.path.basename(folder_path).replace('_', ' ')
        folder_name = 'Pheromone ' + folder_name 
        
        # Plot with different color for each folder
        color = colors[folder_idx % len(colors)]  
        plt.plot(average_data["Timestep"], 
                average_data["Food Found"], 
                label=f"{folder_name}",
                color=color,
                marker='o',
                markersize=1)
    
    plt.xlabel("Timestep")
    plt.ylabel("Food Found")
    plt.title("Average Food Found Over Time")
    plt.grid(True)
    plt.legend()
    full_path = os.path.join(path_where_to_save_graph, graph_name)
    plt.savefig(full_path)
    plt.close()

# Main execution
def main():

    # This part is for choosing 1 folder and save the graph of the files inside that folder
    folder_path = "sim_results/deposit0.0" 
    path_where_to_save_graph = "graphs" 
    graph_name='test1'
    plot_average_food_found_one_folder(folder_path, path_where_to_save_graph, graph_name)



    # This part is for choosing multiple folders
    main_folder = "sim_results"
    path_where_to_save_graph = "graphs"
    graph_name = 'test2'

    # Option A: manually choose sub_folders
    """
    sub_folders = ["decay_and_deposit_0.0", "decay_and_deposit_0.1, ..."]
    """

    # Option B: take all the folders from the main folder
    sub_folders = []
    for file_name in os.listdir(main_folder):
        file_path = os.path.join(file_name)
        sub_folders.append(file_path)  

    plot_average_food_found_multiple_folders(main_folder, sub_folders, path_where_to_save_graph, graph_name)


if __name__ == "__main__":
    main()





