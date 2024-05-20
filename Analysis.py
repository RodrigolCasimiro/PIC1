import matplotlib.pyplot as plt
import numpy as np

def extract_values(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    counts = []
    unix_time_stamps = []
    peak_values = []
    time_stamps = []
    time_since_last = []

    for line in lines:
        parts = line.strip().split()
        counts.append(int(parts[0]))
        unix_time_stamps.append(int(parts[1]))
        peak_values.append(int(parts[2]))
        time_stamps.append(int(parts[3]))
        time_since_last.append(int(parts[4]))

    return counts, unix_time_stamps, peak_values, time_stamps, time_since_last


def analyze_parity(time_since_last):
    total_numbers = len(time_since_last)
    odd_count = sum(1 for number in time_since_last if number % 2 != 0)
    even_count = total_numbers - odd_count

    odd_percentage = (odd_count / total_numbers) * 100
    even_percentage = (even_count / total_numbers) * 100

    print("Method 1 (Parity): ")
    print(f"Percentage of lost bits: {(total_numbers-total_numbers) / total_numbers * 100:.0f}%")
    print(f"Percentage of 1's: {odd_percentage:.4f}%")
    print(f"Percentage of 0's: {even_percentage:.4f}%")


def analyze_pair_parity(time_since_last):
    last_column_values = time_since_last

    ones_count = 0
    zeros_count = 0

    # Iterate over the values in steps of 2
    for i in range(0, len(last_column_values) - 1, 2):
        value1 = last_column_values[i]
        value2 = last_column_values[i + 1]

        if value1 % 2 != 0 and value2 % 2 == 0:
            ones_count += 1
        elif value1 % 2 == 0 and value2 % 2 != 0:
            zeros_count += 1
        # If both are even or both are odd, discard the pair

    total_bits = ones_count + zeros_count

    ones_percentage = (ones_count / total_bits) * 100
    zeros_percentage = (zeros_count / total_bits) * 100
    lost_percentage = ((len(last_column_values) - total_bits) / (len(last_column_values))) * 100

    print("\nMethod 1 Corrected: ")
    print(f"Percentage of lost bits: {lost_percentage:.0f}%")
    print(f"Percentage of 1's: {ones_percentage:.4f}%")
    print(f"Percentage of 0's: {zeros_percentage:.4f}%")


def analyze_intervals(time_since_last):
    intervals = time_since_last

    ones_count = 0
    zeros_count = 0
    # Iterate over the intervals in steps of 2
    for i in range(0, len(intervals) - 1, 2):
        delta_t1 = intervals[i]
        delta_t2 = intervals[i + 1]

        if delta_t1 > delta_t2:
            zeros_count += 1
        elif delta_t1 < delta_t2:
            ones_count += 1
        # If delta_t1 == delta_t2, we discard the event

    total_bits = zeros_count + ones_count

    ones_percentage = (ones_count / total_bits) * 100
    zeros_percentage = (zeros_count / total_bits) * 100

    print("\nMethod 2: ")
    print(f"Percentage of lost bits: {(len(intervals) - total_bits) / len(intervals) * 100:.0f}%")
    print(f"Percentage of 1's: {ones_percentage:.4f}%")
    print(f"Percentage of 0's: {zeros_percentage:.4f}%")


def plot_histogram(peak_values):
    plt.hist(peak_values, bins=20, range=(700, 800), edgecolor='black')
    plt.title('Histogram of Peak Values')
    plt.xlabel('Peak Value')
    plt.ylabel('Frequency')
    plt.show()


def plot_histogram_and_average(time_stamps, counts, interval_minutes, max_interval=None):
    # Convert unix time stamps from milliseconds to minutes
    minutes_since_start = [(ts - time_stamps[0]) / 60000.0 for ts in time_stamps]

    # Determine the maximum interval
    if max_interval is None:
        max_interval = max(minutes_since_start)

    # Define the bin edges for the histogram
    bin_edges = np.arange(0, max_interval + interval_minutes, interval_minutes)

    # Count the number of timeStamps in each bin
    hist, _ = np.histogram(minutes_since_start, bins=bin_edges)

    # Calculate the average counts per interval
    counts_per_bin = np.zeros(len(bin_edges) - 2)  # Exclude the last bin
    for i in range(len(bin_edges) - 2):
        in_bin = [(minutes_since_start[j] >= bin_edges[i]) and (minutes_since_start[j] < bin_edges[i + 1]) for j in range(len(minutes_since_start))]
        if np.sum(in_bin) > 0:
            counts_per_bin[i] = np.mean([counts[j] for j in range(len(counts)) if in_bin[j]])
        else:
            counts_per_bin[i] = 0

    # Calculate the average height of the histogram bars, excluding the last bar
    average_hist_height = np.mean(hist[:-1])

    # Calculate the uncertainty as sqrt(N) for each bin
    uncertainty = np.sqrt(hist[:-1])

    # Plot the histogram of the number of timeStamps, excluding the last bar
    fig, ax1 = plt.subplots(figsize=(12, 6))

    color = 'tab:blue'
    ax1.set_xlabel('Time (minutes)')
    ax1.set_ylabel('Number of Time Stamps', color='black')
    ax1.hist(minutes_since_start, bins=bin_edges[:-1], edgecolor='black', alpha=0.7, label='Number of Time Stamps', color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    # Plot the average height of the histogram bars
    ax1.axhline(average_hist_height, color='red', label='Average Number of Time Stamps')

    # Plot the uncertainty lines
    ax1.axhline(average_hist_height + np.mean(uncertainty), color='orange', linestyle='--', linewidth=0.7, label='Uncertainty (Upper)')
    ax1.axhline(average_hist_height - np.mean(uncertainty), color='orange', linestyle='--', linewidth=0.7, label='Uncertainty (Lower)')

    fig.tight_layout()
    plt.title('Histogram of Time Stamps and Average Counts per Time Interval')
    plt.legend()
    plt.show()


### RUN ###

file_path = 'Data/GeigerDataset_2024-05-11 09:18:27.155241.txt'

# Extract values from the file
counts, unix_time_stamps, peak_values, time_stamps, time_since_last = extract_values(file_path)

# Analyze using the different methods
analyze_parity(time_since_last)
analyze_pair_parity(time_since_last)
analyze_intervals(time_since_last)

# Plot the histogram of peak values
# plot_histogram(peak_values)


# Plot the histogram and average counts
plot_histogram_and_average(time_stamps, counts, 5, 375)