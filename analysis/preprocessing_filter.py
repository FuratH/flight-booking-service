import csv
import statistics
from collections import defaultdict
import os
import shutil

def filter_and_aggregate_csv(input_file, metric_name, output_dir):
    try:
        # Step 1: Read the input CSV and group by name and timestamp
        with open(input_file, 'r') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames

            # Check if required columns exist
            required_columns = {'metric_name', 'metric_value', 'timestamp', 'name'}
            if not required_columns.issubset(fieldnames):
                raise ValueError("The input CSV must contain 'metric_name', 'metric_value', 'timestamp', and 'name' columns.")

            grouped_data = defaultdict(lambda: defaultdict(list))
            timestamps_by_name = defaultdict(list)

            for row in reader:
                if row['metric_name'] == metric_name:
                    name = row['name'].strip("${}/")  # Extract name for file naming
                    
                    if "seats" in name:
                        name = "seats"
                    
                    if "flights?from" in name:
                        name = "flights"

                    timestamp = float(row['timestamp'])  # Convert timestamp to float
                    metric_value = float(row['metric_value'])  # Convert metric_value to float
                    grouped_data[name][timestamp].append(metric_value)
                    timestamps_by_name[name].append(timestamp)

 

        if not grouped_data:
            print(f"No rows found for metric '{metric_name}'.")
            return
        

        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        os.makedirs(output_dir, exist_ok=True)

        for name, data in grouped_data.items():
            timestamps = sorted(timestamps_by_name[name])
            start_time = timestamps[0]

            # Step 2: Aggregate data and adjust timestamps to elapsed time
            aggregated_rows = []
            for timestamp, values in sorted(data.items()):
                median_value = statistics.median(values)
                elapsed_time = timestamp - start_time  # Convert to time elapsed from 0
                aggregated_rows.append({
                    'elapsed_time': elapsed_time,
                    metric_name: median_value
                })

            # Step 3: Write the aggregated data to separate output CSV files per name
            output_file = f"{output_dir}/{name}.csv"

            new_fieldnames = ['elapsed_time', metric_name]

            with open(output_file, 'w', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=new_fieldnames)
                writer.writeheader()
                writer.writerows(aggregated_rows)

            print(f"Aggregated CSV for '{name}' saved to '{output_file}'.")

    except Exception as e:
        print(f"Error: {e}")

# Example usage
metric_name = "http_req_duration"  # Replace with your desired metric name



directories = ["f_run_0t", "f_run_3t", "f_run_6t", "f_run_20t", "f_run_40t", "f_run_60t"]

parentdirectory = "baseline"

for directory in directories:
        output_dir1 = f"./{parentdirectory}/{directory}/3000"
        output_dir2 = f"./{parentdirectory}/{directory}/3001"

        input_file1 = f"./{parentdirectory}/{directory}/client_results_3000.csv"
        input_file2 = f"./{parentdirectory}/{directory}/client_results_3001.csv"

        filter_and_aggregate_csv(input_file1, metric_name, output_dir1)
        filter_and_aggregate_csv(input_file2, metric_name, output_dir2) 


