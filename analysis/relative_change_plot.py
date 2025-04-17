import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def read_csv(file_path):
    """Reads the CSV file and converts necessary columns to numeric."""
    df = pd.read_csv(file_path, low_memory=False)
    df['http_req_duration'] = pd.to_numeric(df['http_req_duration'], errors='coerce')
    df['elapsed_time'] = pd.to_numeric(df['elapsed_time'], errors='coerce')
    return df

def filter_warmup_cooldown(df, warmup_time, cooldown_time):
    """Filters out the warm-up and cool-down phases from the dataset."""
    experiment_start = df['elapsed_time'].min() + warmup_time
    experiment_end = df['elapsed_time'].max() - cooldown_time
    return df[(df['elapsed_time'] >= experiment_start) & (df['elapsed_time'] <= experiment_end)]

def plot_relative_change(file1, file2, warmup_time=60, cooldown_time=60, window_size=10):
    """Plots the relative percentage change between two runs using small time windows."""
    
    # Read and filter the data
    data1 = filter_warmup_cooldown(read_csv(file1), warmup_time, cooldown_time)
    data2 = filter_warmup_cooldown(read_csv(file2), warmup_time, cooldown_time)
    
    # Aggregate data in small time windows
    data1['time_window'] = (data1['elapsed_time'] // window_size) * window_size
    data2['time_window'] = (data2['elapsed_time'] // window_size) * window_size
    
    grouped1 = data1.groupby('time_window')['http_req_duration'].median().reset_index()
    grouped2 = data2.groupby('time_window')['http_req_duration'].median().reset_index()
    
    # Merge on time_window to compute relative change
    merged_data = pd.merge(grouped1, grouped2, on='time_window', suffixes=('_run1', '_run2'))
    
    # Compute relative change
    merged_data['relative_change'] = ((merged_data['http_req_duration_run2'] - merged_data['http_req_duration_run1']) 
                                      / merged_data['http_req_duration_run1']) * 100
    
    # Create plot
    plt.figure(figsize=(7, 7))
    
    # Highlight the noise period in the background
    plt.axvspan(200, 500, color='red', alpha=0.1, label='Noise Influence Period')
    
    # Plot the relative change
    sns.lineplot(data=merged_data, x='time_window', y='relative_change', color='green', label='Relative Change (%)', linewidth=0.8)
    plt.ylabel('Relative Change (%)', color='green')
    
    # Plot settings
    plt.xlabel('Elapsed Time (seconds)', fontsize=14)
    plt.title('Relative Change Between Runs - Baseline (Seats)', fontsize=14)
    plt.legend(fontsize=12)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)     
    plt.grid(True)
    plt.show()


# Example usage:
file1 = "./core_isolation/f_run_3t/3000/destinations.csv"
file2 = "./core_isolation/f_run_3t/3001/destinations.csv"

plot_relative_change(file1, file2, warmup_time=60, cooldown_time=150, window_size=1)
