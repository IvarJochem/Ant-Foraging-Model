import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy.stats import f_oneway, shapiro
import pandas as pd
from statsmodels.stats.multicomp import pairwise_tukeyhsd



def find_header_index(file_path):
    """
    Find the header in the txt file to know how many rows to skip 
    """
    with open(file_path, 'r') as file:
        for i, line in enumerate(file):
            if 'Timestep, Food Found, AntsFood' in line:
                return i + 1
    return 0


def plot_average_food_found_multiple_folders(main_folder, sub_folders, path_where_to_save_graph, graph_name):
    """
    Load multiple files from multiple folders, calculate the average Food Found and standard deviation
    for each timestep per folder, and plot all results in one graph with improved line visibility.
    """

    column_names = ["Timestep", "Food Found", "AntsFood"]

    plt.figure(figsize=(12, 8))  
    line_style = '-'

    colors = ['#1f77b4', '#d62728', '#2ca02c', '#9467bd', '#ff7f0e']
    
    
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
        
        # Calculate average and standard deviation for this folder
        grouped = combined_data.groupby("Timestep")
        average_data = grouped.mean().reset_index()
        std_data = grouped.std().reset_index()
        
        # Folder name for legend
        folder_name = os.path.basename(folder_path)
        folder_name = 'Pheromone ' + folder_name 
        folder_name = folder_name.replace('deposit', 'deposit: ')
        folder_name = folder_name.replace('_', ' ')
        
        color = colors[folder_idx % len(colors)]
        
        # Plot the mean line 
        plt.plot(average_data["Timestep"], 
                average_data["Food Found"], 
                label=f"{folder_name}",
                color=color,
                linestyle=line_style,
                linewidth=2)  
        
        # Shaded area for standard deviation 
        plt.fill_between(average_data["Timestep"],
                        average_data["Food Found"] - std_data["Food Found"],
                        average_data["Food Found"] + std_data["Food Found"],
                        color=color,
                        alpha=0.1)  

    plt.xlabel("Timestep", fontsize=12)
    plt.ylabel("Food found", fontsize=12)
    plt.title("Average food found over time\n(±1 Std Dev)", fontsize=14)
    plt.grid(True, alpha=0.3)  
    plt.legend(loc='upper left', fontsize=12)
    plt.tight_layout()
    
    full_path = os.path.join(path_where_to_save_graph, graph_name)
    plt.savefig(full_path, bbox_inches='tight')  
    plt.close()


def food_found_last_timestep_per_group(main_folder, sub_folders):
    """
    Load multiple files from multiple folders and return a dictionary of lists
    where each key is a group (subfolder) and the value is a list of food found 
    at the last timestep for each file in that group.
    """
    column_names = ["Timestep", "Food Found", "AntsFood"]
    results = {}
    
    for folder_path in sub_folders:
        all_last_food_found = []
        
        # Get the full path of the subfolder
        sub_folder_path = os.path.join(main_folder, folder_path)
        if not os.path.exists(sub_folder_path):
            print(f"Folder does not exist: {sub_folder_path}")
            continue  # Skip to the next subfolder
        
        # Iterate over all .txt files in the folder
        for file_name in os.listdir(sub_folder_path):
            file_path = os.path.join(sub_folder_path, file_name)
            
            if os.path.isfile(file_path) and file_name.endswith('.txt'):
                skiprows = find_header_index(file_path=file_path)
                data = pd.read_csv(file_path, skiprows=skiprows, names=column_names)
                
                # Get the food found at the last timestep
                last_food_found = data["Food Found"].iloc[-1]
                all_last_food_found.append(last_food_found)
        
        if not all_last_food_found:
            print(f"No valid files found in folder: {folder_path}")
            continue
        
        # Store all values for this group
        results[folder_path] = all_last_food_found
    
    return results

def shapiro_test(grouped_data):
    """
    Perform Shapiro-Wilk test for normality for each group in the data. Necessary for performing anova test
    """
    print("Shapiro-Wilk Test Results:")
    for group, data in grouped_data.items():
        stat, p_value = shapiro(data)
        print(f"Group: {group} | W-statistic: {stat:.4f}, P-value: {p_value:.4f}")
        if p_value < 0.05:
            print(f"  -> The data in {group} is NOT normally distributed (p < 0.05).")
        else:
            print(f"  -> The data in {group} is normally distributed (p >= 0.05).")
    print()
    return

def anova_test(grouped_data):
    """
    Perform one sided anova test
    """
    group_0 = grouped_data["deposit0.0"]
    group_02 = grouped_data["deposit0.2"]
    group_04 = grouped_data["deposit0.4"]
    group_06 = grouped_data["deposit0.6"]
    group_08 = grouped_data["deposit0.8"]

    # One-way ANOVA
    f_stat, p_value = f_oneway(group_0, group_02, group_04, group_06, group_08)
    print(f"F-statistic: {f_stat}")
    print(f"P-value: {p_value}")

    return


def tukeys_test(grouped_data):

    # Prepare data for Tukey's HSD
    all_data = []
    group_labels = []
    for label, values in grouped_data.items():
        all_data.extend(values)
        group_labels.extend([label] * len(values))

    df = pd.DataFrame({"Decay Group": group_labels, "Food Found": all_data})

    # Tukey's HSD
    tukey = pairwise_tukeyhsd(endog=df["Food Found"], groups=df["Decay Group"], alpha=0.05)
    print(tukey)

    return 

def main():
    # Main execution
    
    main_folder = 'sim_results/'
    path_where_to_save_graph = "graphs"
    graph_name = ''

    # Option A: manually choose sub_folders
    sub_folders = ["deposit0.0", "deposit0.2", "deposit0.4", "deposit0.6", "deposit0.8"]

    # Option B: take all the folders from the main folder
    """
    sub_folders = []
    for file_name in os.listdir(main_folder):
        file_path = os.path.join(file_name)
        sub_folders.append(file_path)  
    """

    plot_average_food_found_multiple_folders(main_folder, sub_folders, path_where_to_save_graph, graph_name)

    grouped_data = food_found_last_timestep_per_group(main_folder, sub_folders)

    shapiro_test(grouped_data=grouped_data)
    anova_test(grouped_data=grouped_data)
    tukeys_test(grouped_data=grouped_data)

if __name__ == "__main__":
    main()





