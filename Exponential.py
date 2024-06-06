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
                column_data.append(int(columns[column_index]))

    return column_data

# Function to estimate lambda and generate exponential random numbers, accounting for dead time
def generate_exponential_random(data, target_lambda, dead_time=18):
    sum_intervals = 0
    intervals = []
    random_values = []

    # Adjust for dead time and update sum of intervals and intervals list
    for interval in data:
        if interval > dead_time:
            adjusted_interval = interval - dead_time
            intervals.append(adjusted_interval)
            sum_intervals += adjusted_interval

            # Calculate mean interval and estimate lambda
            mean_interval = sum_intervals / len(intervals)
            lambda_estimate = 1.0 / mean_interval

            # Scale to target lambda
            scaled_interval = adjusted_interval * (1000 * lambda_estimate / target_lambda)
            random_values.append(scaled_interval)

    return random_values

# File path to the data file
file_path = 'Data/GeigerDataset_2024-05-24 09:31:24.691587.txt'

# Extract the 5th column (index 4 as it's 0-based)
column_index = 4
data = extract_column(file_path, column_index)

# Convert the list to a numpy array for further processing if needed
data_array = np.array(data)

# Example target lambda
target_lambda = float(input("Enter the average number of counts per second: "))

# Generate exponential random numbers using the extracted data
random_numbers = generate_exponential_random(data_array, target_lambda)

# Plot histogram of the generated random numbers using matplotlib
plt.figure(figsize=(10, 6))
plt.hist(random_numbers, bins=50, alpha=0.7, edgecolor='black')

plt.xlabel('Random Number Value')
plt.ylabel('N')
plt.title('Histogram of Generated Exponential')
plt.show()
