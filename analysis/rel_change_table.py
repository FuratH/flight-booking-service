import pandas as pd
import scipy.stats as stats
import numpy as np

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

def bootstrap_relative_change(data1, data2, n_bootstrap=10000, ci=0.99):
    """Calculates confidence intervals for the relative change using bootstrapping."""
    boot_rel_changes = [
        np.median(np.random.choice(data2, size=len(data2), replace=True)) /
        np.median(np.random.choice(data1, size=len(data1), replace=True))
        for _ in range(n_bootstrap)
    ]
    lower_bound = np.percentile(boot_rel_changes, (1 - ci) / 2 * 100)
    upper_bound = np.percentile(boot_rel_changes, (1 + ci) / 2 * 100)
    mean_ratio = np.mean(boot_rel_changes)
    return float(lower_bound), float(upper_bound), float(mean_ratio)

def calculate_median_changes(data, noise_start=200, noise_end=500):
    """Calculates medians for noise and non-noise periods."""
    noise_data = data[(data['elapsed_time'] >= noise_start) & (data['elapsed_time'] <= noise_end)]
    non_noise_data = data[(data['elapsed_time'] < noise_start) | (data['elapsed_time'] > noise_end)]

    noise_median = noise_data['http_req_duration'].median()
    non_noise_median = non_noise_data['http_req_duration'].median()
    overall_median = data['http_req_duration'].median()

    return noise_median, non_noise_median, overall_median

def analyze_response_times(file1, file2, endpoint, threads=3, warmup_time=60, cooldown_time=60):
    """Analyzes the median response times and relative changes between noise and non-noise phases."""
    data1 = filter_warmup_cooldown(read_csv(file1), warmup_time, cooldown_time)
    data2 = filter_warmup_cooldown(read_csv(file2), warmup_time, cooldown_time)

    noise_m1, non_noise_m1, overall_m1 = calculate_median_changes(data1)
    noise_m2, non_noise_m2, overall_m2 = calculate_median_changes(data2)

    # Bootstrapped confidence intervals and ratio means
    noise_data1 = data1[(data1['elapsed_time'] >= 200) & (data1['elapsed_time'] <= 500)]
    noise_data2 = data2[(data2['elapsed_time'] >= 200) & (data2['elapsed_time'] <= 500)]
    non_noise_data1 = data1[(data1['elapsed_time'] < 200) | (data1['elapsed_time'] > 500)]
    non_noise_data2 = data2[(data2['elapsed_time'] < 200) | (data2['elapsed_time'] > 500)]

    ci_n = bootstrap_relative_change(noise_data1['http_req_duration'], noise_data2['http_req_duration'])
    ci_nn = bootstrap_relative_change(non_noise_data1['http_req_duration'], non_noise_data2['http_req_duration'])
    ci_overall = bootstrap_relative_change(data1['http_req_duration'], data2['http_req_duration'])

    # Mann-Whitney U Test for statistical significance
    p_noise = stats.mannwhitneyu(noise_data1['http_req_duration'], noise_data2['http_req_duration'], alternative='two-sided').pvalue
    p_non_noise = stats.mannwhitneyu(non_noise_data1['http_req_duration'], non_noise_data2['http_req_duration'], alternative='two-sided').pvalue
    p_overall = stats.mannwhitneyu(data1['http_req_duration'], data2['http_req_duration'], alternative='two-sided').pvalue

    # Relative changes using median
    relative_change_noise = noise_m2 / noise_m1 if noise_m1 != 0 else float('nan')
    relative_change_non_noise = non_noise_m2 / non_noise_m1 if non_noise_m1 != 0 else float('nan')
    relative_change_overall = overall_m2 / overall_m1 if overall_m1 != 0 else float('nan')

    # Relative Confidence Interval Widths (RCIW)
    def calc_rciw(ci_tuple):
        lower, upper, ratio = ci_tuple
        if ratio == 0 or np.isnan(ratio):
            return float('nan')
        return (upper - lower) / ratio

    rciw_noise = calc_rciw(ci_n)
    rciw_non_noise = calc_rciw(ci_nn)
    rciw_overall = calc_rciw(ci_overall)

    # Format CI strings
    ci_n_str = f"{ci_n[0]:.4f} - {ci_n[1]:.4f}"
    ci_nn_str = f"{ci_nn[0]:.4f} - {ci_nn[1]:.4f}"
    ci_overall_str = f"{ci_overall[0]:.4f} - {ci_overall[1]:.4f}"

    return {
        'Endpoint': endpoint,
        'Threads': threads,
        'Run1 Median': float(overall_m1),
        'Run1 Median Noise': float(noise_m1),
        'Run1 Median Non-Noise': float(non_noise_m1),
        'Run2 Median': float(overall_m2),
        'Run2 Median Noise': float(noise_m2),
        'Run2 Median Non-Noise': float(non_noise_m2),
        'Relative Change Noise Phase': f'{relative_change_noise:.4f} (CI: {ci_n_str})',
        'Relative Change Non-Noise Phase': f'{relative_change_non_noise:.4f} (CI: {ci_nn_str})',
        'Relative Change Overall': f'{relative_change_overall:.4f} (CI: {ci_overall_str})',
        'CI Noise': (ci_n[0], ci_n[1]),
        'CI Non-Noise': (ci_nn[0], ci_nn[1]),
        'CI Overall': (ci_overall[0], ci_overall[1]),
        'RCIW Noise': rciw_noise,
        'RCIW Non-Noise': rciw_non_noise,
        'RCIW Overall': rciw_overall,
        'P-Value Noise': p_noise,
        'P-Value Non-Noise': p_non_noise,
        'P-Value Overall': p_overall
    }

def dataframe_to_latex(df, caption="Table Caption", label="tab:label"):
    """Convert a DataFrame to a LaTeX tabular format with resizing and highlighting."""
    def escape_latex(text):
        if isinstance(text, str):
            escape_dict = {
                "$": "\$",
                "_": "\_",
                "&": "\&",
                "#": "\#",
                "%": "\%",
                "{": "\{",
                "}": "\}"
            }
            for char, replacement in escape_dict.items():
                text = text.replace(char, replacement)
        else:
            text = str(text)
        return text

    def highlight_outliers(value, ci):
        try:
            lower, upper = ci
            if lower > 1 or 1 > upper:
                return f"\\textbf{{{value}}}"
        except (ValueError, IndexError):
            pass
        return value

    def highlight_pvalue(pval):
        if pd.notnull(pval) and pval < 0.01:
            return f"\\textbf{{{pval:.4f}}}"
        return f"{pval:.4f}" if pd.notnull(pval) else "NaN"

    # Escape LaTeX characters
    df = df.copy()
    df.index = df.index.map(escape_latex)
    df.columns = df.columns.map(escape_latex)

    # Highlight outliers
    for index, row in df.iterrows():
        df.at[index, 'Relative Change Noise Phase'] = highlight_outliers(row['Relative Change Noise Phase'], row['CI Noise'])
        df.at[index, 'Relative Change Non-Noise Phase'] = highlight_outliers(row['Relative Change Non-Noise Phase'], row['CI Non-Noise'])
        df.at[index, 'Relative Change Overall'] = highlight_outliers(row['Relative Change Overall'], row['CI Overall'])

    # Format RCIW and P-Values
    df['RCIW Noise'] = df['RCIW Noise'].apply(lambda x: f"{x:.4f}" if pd.notnull(x) else "NaN")
    df['RCIW Non-Noise'] = df['RCIW Non-Noise'].apply(lambda x: f"{x:.4f}" if pd.notnull(x) else "NaN")
    df['RCIW Overall'] = df['RCIW Overall'].apply(lambda x: f"{x:.4f}" if pd.notnull(x) else "NaN")

    df['P-Value Noise'] = df['P-Value Noise'].apply(highlight_pvalue)
    df['P-Value Non-Noise'] = df['P-Value Non-Noise'].apply(highlight_pvalue)
    df['P-Value Overall'] = df['P-Value Overall'].apply(highlight_pvalue)

    # Drop CI columns before export
    df = df.drop(columns=['CI Noise', 'CI Non-Noise', 'CI Overall'])

    # Generate LaTeX table
    latex_table = df.to_latex(
        float_format="%.4f",
        caption=caption,
        label=label,
        bold_rows=False,
        index=True
    )

    latex_table = (
        "\\begin{table}[h]\n"
        "\\centering\n"
        f"\\caption{{{caption}}}\n"
        f"\\label{{{label}}}\n"
        "\\resizebox{1\\linewidth}{!}{%\n"
        f"{latex_table}\n"
        "}\n"
        "\\end{table}"
    )

    return latex_table

# === Execution Section ===

directories = ["f_run_0t", "f_run_3t", "f_run_6t", "f_run_20t", "f_run_40t", "f_run_60t"]

experiment_files = {
    "bookings": ["3000/bookings.csv", "3001/bookings.csv"],
    "destinations": ["3000/destinations.csv", "3001/destinations.csv"],
    "flights": ["3000/flights.csv", "3001/flights.csv"],
    "seats": ["3000/seats.csv", "3001/seats.csv"]
}

results = []

for directory in directories:
    try:
        threads = int(directory.split('_')[2].replace('t', ''))
    except ValueError:
        print(f"Error parsing threads from directory name: {directory}")
        continue

    for endpoint, files in experiment_files.items():
        file1 = f"./microvm/{directory}/{files[0]}"
        file2 = f"./microvm/{directory}/{files[1]}"
        result = analyze_response_times(file1, file2, endpoint=endpoint, threads=threads, warmup_time=60, cooldown_time=150)
        results.append(result)

final_table = pd.DataFrame(results)
print(final_table)
final_table.to_csv("rel_table_multiple_endpoints.csv", index=False)
print(dataframe_to_latex(final_table, caption="Response Time Comparison", label="tab:response_times"))
