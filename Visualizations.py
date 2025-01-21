import pandas as pd
import matplotlib.pyplot as plt
import os


# Function to load and split data by run from the text file
def load_data(file_path, column_names):
    """
    Load and split simulation data by run from the text file.
    """
    # Read the entire file into a DataFrame
    data = pd.read_csv(file_path, skiprows=7, names=column_names)

    return data


def plot_average_food_found(folder_path, column_names):
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


# Main execution
def main():
    folder_path = "sim_results"  # Folder containing the files
    column_names = ["Timestep", "Food Found", "AntsFood"]
    plot_average_food_found(folder_path, column_names)


if __name__ == "__main__":
    main()





