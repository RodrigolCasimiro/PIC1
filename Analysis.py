import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

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


def analyze_intervals(time_since_last, Steps = 1):
    intervals = time_since_last

    ones_count = 0
    zeros_count = 0
    # Iterate over the intervals in steps of 2
    for i in range(0, len(intervals) - 1, Steps):
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

    print(f"\nMethod 2 (Step of {Steps}): ")
    print(f"Percentage of lost bits: {(len(intervals) - total_bits) / len(intervals) * 100:.0f}%")
    print(f"Percentage of 1's: {ones_percentage:.4f}%")
    print(f"Percentage of 0's: {zeros_percentage:.4f}%")


def plot_histogram(peak_values):
    plt.figure(num='Histogram of Peak Values')
    plt.hist(peak_values, bins=20, range=(700, 800), edgecolor='black')
    plt.title('Histogram of Peak Values')
    plt.xlabel('Peak Value')
    plt.ylabel('Frequency')
    plt.show(block = False)


def plot_histogram_and_average(time_stamps, counts, interval_minutes, max_interval=None, zoom=False, num_bins=10):
    # Create the figure and axes based on the zoom parameter
    if zoom:
        fig, (ax2, ax1) = plt.subplots(1, 2, figsize=(18, 6), gridspec_kw={'width_ratios': [1, 5]})
    else:
        fig, ax1 = plt.subplots(1, 1, figsize=(12, 6))

    # Convert time stamps from milliseconds to minutes
    minutes_since_start = (np.array(time_stamps) - time_stamps[0]) / 60000.0

    # Determine the maximum interval
    if max_interval is None:
        max_interval = np.max(minutes_since_start)

    # Define the bin edges for the histogram
    bin_edges = np.arange(0, max_interval + interval_minutes, interval_minutes)

    # Count the number of time stamps in each bin
    hist, _ = np.histogram(minutes_since_start, bins=bin_edges)

    # Calculate the average height of the histogram bars, excluding the last bar
    average_hist_height = np.mean(hist[:-1])

    # Calculate the uncertainty as sqrt(N) for each bin
    uncertainty = np.sqrt(hist[:-1])

    # Plot the histogram of the number of time stamps
    color = 'tab:blue'
    ax1.hist(minutes_since_start, bins=bin_edges[:-1], edgecolor='black', alpha=0.7, label='Number of Time Stamps', color=color)
    ax1.set_xlabel('Time (minutes)')
    #ax1.set_ylabel('Number of Time Stamps', color='black')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_yticklabels([])
    ax1.tick_params(axis='y', left=False)


    # Plot the average height and uncertainty lines
    plot_uncertainty_lines(ax1, average_hist_height, uncertainty)

    # Set title and legend for the histogram plot
    ax1.set_title('Histogram of Time Stamps and Average Counts per Time Interval')
    ax1.legend()

    # Adjust y-axis limits if zoom is enabled
    if zoom:
        upper = average_hist_height + zoom * np.mean(uncertainty)
        lower = average_hist_height - zoom * np.mean(uncertainty)
        ax1.set_ylim(lower, upper)
        ax2.set_ylim(lower, upper)

        # Create a projection of the bar heights
        unique_heights, counts = np.unique(hist, return_counts=True)
        plot_projection(ax2, unique_heights, counts, average_hist_height, uncertainty, num_bins)

    # Show plots
    plt.tight_layout()
    plt.show(block=False)


def plot_uncertainty_lines(ax, average_height, uncertainty):
    """
    Plots the average height and uncertainty lines on the given axis.
    """
    sdp1 = average_height + np.mean(uncertainty)
    sdn1 = average_height - np.mean(uncertainty)
    sdp2 = average_height + 2 * np.mean(uncertainty)
    sdn2 = average_height - 2 * np.mean(uncertainty)

    ax.axhline(average_height, color='orange', label='Average Number of Time Stamps')
    ax.axhline(sdp1, color='orange', ls='--', lw=0.7)
    ax.axhline(sdn1, color='orange', ls='--', lw=0.7, label='Uncertainty')
    ax.axhline(sdp2, color='orange', ls=':', lw=0.5)
    ax.axhline(sdn2, color='orange', ls=':', lw=0.5)


def plot_projection(ax, unique_heights, counts, average_height, uncertainty, num_bins):
    """
    Plots the projection of bar heights on the given axis.
    """
    # Adjust number of bins for the projection plot
    bin_width = (max(unique_heights) - min(unique_heights)) / num_bins
    bins = np.arange(min(unique_heights), max(unique_heights) + bin_width, bin_width)

    # Plot the projection histogram
    ax.hist(unique_heights, bins=bins, weights=counts, edgecolor='black', alpha=0.7, orientation='horizontal')
    ax.set_xlabel('Frequency')
    ax.set_ylabel('Number of Counts')
    ax.set_title('Projection of Bar Heights')

    # Plot the average height and uncertainty lines on the projection plot
    sdp1 = average_height + np.mean(uncertainty)
    sdn1 = average_height - np.mean(uncertainty)
    sdp2 = average_height + 2 * np.mean(uncertainty)
    sdn2 = average_height - 2 * np.mean(uncertainty)

    ax.axhline(average_height, color='orange')
    ax.axhline(sdp1, color='orange', ls='--', lw=0.7)
    ax.axhline(sdn1, color='orange', ls='--', lw=0.7)
    ax.axhline(sdp2, color='orange', ls=':', lw=0.5)
    ax.axhline(sdn2, color='orange', ls=':', lw=0.5)


def find_min_and_count(time_since_last):
    min_value = min(time_since_last)
    count_min_value = time_since_last.count(min_value)

    print(f"\nThe Geiger dead time is {min_value} and it appears {count_min_value} times in the list.")

### RUN ###

file_path = 'Data/GeigerDataset_2024-05-11 09:18:27.155241.txt'

# Extract values from the file
counts, unix_time_stamps, peak_values, time_stamps, time_since_last = extract_values(file_path)

# Analyze using the different methods
analyze_parity(time_since_last)
analyze_pair_parity(time_since_last)
analyze_intervals(time_since_last)
analyze_intervals(time_since_last, 2)

# Dead time
find_min_and_count(time_since_last)

# Plot the histogram of peak values
plot_histogram(peak_values)

# Plot the histogram and average counts
interval_minutes = 3
max_interval = 374

# Plot the histogram and average counts
interval_minutes = 5
max_interval = 374
plot_histogram_and_average(time_stamps, counts, interval_minutes, max_interval, zoom=3)

# Show plots
plt.show()