import numpy as np
import matplotlib.pyplot as plt

def extract_column(file_path, column_index):
    # Initialize a list to store the data from the specified column
    column_data = []

    # Open the file and read the data
    with open(file_path, 'r') as file:
        for line in file:
            # Split the line into columns based on whitespace
            columns = line.split()

            # Ensure there are enough columns in the line
            if len(columns) > column_index:
                # Append the value from the specified column to the list
                column_data.append(float(columns[column_index]))

    return column_data

def update_poisson_plot(time_stamps, desired_avg_counts):
    """Updates the Poisson plot based on the counts accumulated in fixed time intervals, excluding the last incomplete interval."""
    if len(time_stamps) > 0:
        # Determine the time range from the first to the last timestamp
        first_timestamp = time_stamps[0]
        last_timestamp = time_stamps[-1]

        # Calculate the total duration
        total_duration = last_timestamp - first_timestamp

        # Calculate the total number of events
        total_events = len(time_stamps)

        # Calculate the event rate (events per millisecond)
        event_rate = total_events / total_duration

        # Calculate the interval size to achieve the desired average counts
        interval_size = desired_avg_counts / event_rate

        # Calculate the total number of intervals, considering only completed intervals
        num_intervals = int(total_duration // interval_size)
        counts = [0] * num_intervals

        # Count the timestamps in each interval
        for ts in time_stamps:
            interval_index = int((ts - first_timestamp) // interval_size)
            if interval_index < num_intervals:  # This ensures we do not count into the last, potentially unfinished interval
                counts[interval_index] += 1

        return counts, interval_size
    return [], 0

# Input for desired average counts per interval
desired_avg_counts = 1.5  # Change this value as needed

# File path to the data file
file_path = 'Data/GeigerDataset_2024-05-24 09:31:24.691587.txt'
column_index = 3  # 4th column (0-based index)
time_stamps = extract_column(file_path, column_index)

counts, interval_size = update_poisson_plot(time_stamps, desired_avg_counts)

# Plot the Poisson distribution using a histogram
plt.figure(figsize=(10, 6))
plt.hist(counts, bins=range(0, max(counts) + 2), alpha=0.7, edgecolor='black')

plt.xlabel('Number of Counts per Time Interval')
plt.ylabel('N')
plt.title(f'Poisson Distribution of Counts per Interval (Interval Size: {interval_size:.2f} ms)')
plt.show()