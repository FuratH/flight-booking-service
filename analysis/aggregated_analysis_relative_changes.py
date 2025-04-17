import pandas as pd
import os
import numpy as np
from scipy.stats import bootstrap

def load_csv(file_path):
    """Load CSV file into a DataFrame."""
    return pd.read_csv(file_path)

def split_phases(df):
    """Split data into pre-noise, noise, and post-noise phases."""
    pre_noise = df[df['elapsed_time'] < 200]
    noise = df[(df['elapsed_time'] >= 200) & (df['elapsed_time'] <= 500)]
    post_noise = df[df['elapsed_time'] > 500]
    return pre_noise, noise, post_noise

def compute_median(df):
    """Compute the median http_req_duration."""
    return df['http_req_duration'].median()

def compute_ratio_ci(df_v1, df_v2):
    """Compute the 99% confidence interval for the ratio of medians using bootstrapping."""
    if len(df_v1) == 0 or len(df_v2) == 0:
        return (np.nan, np.nan)

    def median_ratio(v1, v2):
        return np.median(v2) / np.median(v1) if np.median(v1) != 0 else np.nan

    res = bootstrap((df_v1['http_req_duration'].values, df_v2['http_req_duration'].values),
                    statistic=median_ratio, confidence_level=0.99, method='percentile')
    return res.confidence_interval.low, res.confidence_interval.high

def analyze_experiment(parent, baseline_files, experiment_files, directory):
    results = {"pre_noise": [], "noise": [], "post_noise": []}

    for experiment in experiment_files:
        for endpoint, files in experiment.items():
            baseline_v1 = load_csv(baseline_files[0][endpoint][0])
            baseline_v2 = load_csv(baseline_files[0][endpoint][1])
            exp_v1 = load_csv(files[0])
            exp_v2 = load_csv(files[1])

            print(baseline_files[0][endpoint][0])
            print(files[0])

            for i, phase_name in enumerate(["pre_noise", "noise", "post_noise"]):
                baseline_phase_v1 = split_phases(baseline_v1)[i]
                baseline_phase_v2 = split_phases(baseline_v2)[i]
                exp_phase_v1 = split_phases(exp_v1)[i]
                exp_phase_v2 = split_phases(exp_v2)[i]

                median_baseline_v1 = compute_median(baseline_phase_v1)
                median_baseline_v2 = compute_median(baseline_phase_v2)
                median_exp_v1 = compute_median(exp_phase_v1)
                median_exp_v2 = compute_median(exp_phase_v2)

                relative_change_exp = median_exp_v2 / median_exp_v1 if median_exp_v1 != 0 else np.nan
                relative_change_baseline = median_baseline_v2 / median_baseline_v1 if median_baseline_v1 != 0 else np.nan

                ci_exp = compute_ratio_ci(exp_phase_v1, exp_phase_v2)
                ci_baseline = compute_ratio_ci(baseline_phase_v1, baseline_phase_v2)


                threads = (directory.split('_')[2].replace('t', ''))

                name = parent + " " + threads + "t"
                results[phase_name].append([
                    name,  
                    endpoint,
                    median_exp_v1,
                    median_exp_v2,
                    relative_change_exp,
                    ci_exp[0], ci_exp[1],
                    median_baseline_v1,
                    median_baseline_v2,
                    relative_change_baseline,
                    ci_baseline[0], ci_baseline[1]
                ])

    return results

def display_results(results, parent):
    """Display results in table format and save to CSV."""
    for phase, data in results.items():
        df = pd.DataFrame(data, columns=[
            "Experiment Type", "Endpoint", "Median V1", "Median V2", "Relative Change Exp",
            "CI Exp Lower", "CI Exp Upper", "Baseline Median V1", "Baseline Median V2",
            "Relative Change Baseline", "CI Baseline Lower", "CI Baseline Upper"
        ])
        print(f"\n{phase.upper()} PHASE")
        print(df.to_string(index=False))

        # Save the results to a CSV file in the parent directory
        output_path = os.path.join(parent, f"{phase}.csv")

        # Check if the file already exists
        if os.path.exists(output_path):
            # Append the new data to the existing file
            df.to_csv(output_path, mode='a', header=False, encoding='utf-8', index=False)
        else:
            # Create a new file with the data
            df.to_csv(output_path, encoding='utf-8', index=False)



directories = ["f_run_0t", "f_run_3t", "f_run_6t", "f_run_20t", "f_run_40t", "f_run_60t"]

parent = "core_isolation"
# Iterate over each directory and run the analysis
for directory in directories:
    experiment_files = [
        {
            "bookings": [f"./{parent}/{directory}/3000/bookings.csv", f"./{parent}/{directory}/3001/bookings.csv"],
            "destinations": [f"./{parent}/{directory}/3000/destinations.csv", f"./{parent}/{directory}/3001/destinations.csv"],
            "flights": [f"./{parent}/{directory}/3000/flights.csv", f"./{parent}/{directory}/3001/flights.csv"],
            "seats": [f"./{parent}/{directory}/3000/seats.csv", f"./{parent}/{directory}/3001/seats.csv"]
        }
    ]

    # Define file paths
    baseline_files = [
        {
            "bookings": [f"./baseline/{directory}/3000/bookings.csv", f"./baseline/{directory}/3001/bookings.csv"],
            "destinations": [f"./baseline/{directory}/3000/destinations.csv", f"./baseline/{directory}/3001/destinations.csv"],
            "flights": [f"./baseline/{directory}/3000/flights.csv", f"./baseline/{directory}/3001/flights.csv"],
            "seats": [f"./baseline/{directory}/3000/seats.csv", f"./baseline/{directory}/3001/seats.csv"]
        }
    ]

    # Run analysis
    results = analyze_experiment(parent, baseline_files, experiment_files, directory)
    display_results(results, parent)
