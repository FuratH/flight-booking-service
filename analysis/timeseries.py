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

def plot_median_response_time(file1, file2, warmup_time=60, cooldown_time=60):
    """Plots the filtered time series for two runs and the aggregated median response time,
    while highlighting the noise phase."""
    
    # Read and filter the data
    data1 = filter_warmup_cooldown(read_csv(file1), warmup_time, cooldown_time)
    data2 = filter_warmup_cooldown(read_csv(file2), warmup_time, cooldown_time)
    
    # Combine the filtered data from both runs
    combined_data = pd.concat([data1, data2], ignore_index=True)
    
    # Compute median response time per elapsed_time interval
    median_response = combined_data.groupby('elapsed_time')['http_req_duration'].median().reset_index()

    # Create plot
    plt.figure(figsize=(7, 7))

    # Highlight the noise period in the background
    plt.axvspan(200, 500, color='red', alpha=0.1, label='Noise Influence Period')

    # Plot the filtered response times from both runs
    sns.lineplot(data=data1, x='elapsed_time', y='http_req_duration', color='blue', alpha=1, linewidth=0.8, label='Run 1')
    sns.lineplot(data=data2, x='elapsed_time', y='http_req_duration', color='orange', alpha=1, linewidth=0.8, label='Run 2')

    # Plot the aggregated median response time as a single black line
    #sns.lineplot(data=median_response, x='elapsed_time', y='http_req_duration', color='black', label='Median Response Time')

# Plot settings with larger fonts
    plt.xlabel('Elapsed Time (seconds)', fontsize=14)
    plt.ylabel('HTTP Request Duration (ms)', fontsize=14)
    plt.title('Time Series Comparison - Baseline (Flights)', fontsize=18)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.show()


file1 = "./core_isolation/f_run_3t/3000/destinations.csv"
file2 = "./core_isolation/f_run_3t/3001/destinations.csv"

plot_median_response_time(file1, file2, warmup_time=60, cooldown_time=150)



