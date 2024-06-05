def extract_last_column_values(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    last_column_values = []

    for line in lines:
        parts = line.strip().split()
        last_column_values.append(int(parts[-1]))  # Extracting the last column value

    return last_column_values

def parity_binary(values):
    binary_values = [(1 if value % 2 != 0 else 0) for value in values]
    return binary_values

def pair_parity_binary(time_since_last):
    last_column_values = time_since_last

    ones_count = 0
    zeros_count = 0
    numbers = []
    # Iterate over the values in steps of 2
    for i in range(0, len(last_column_values) - 1, 2):
        value1 = last_column_values[i]
        value2 = last_column_values[i + 1]

        if value1 % 2 != 0 and value2 % 2 == 0:
            ones_count += 1
            numbers.append(1)
        elif value1 % 2 == 0 and value2 % 2 != 0:
            zeros_count += 1
            numbers.append(0)
        # If both are even or both are odd, discard the pair

    return numbers

def intervals_binary(time_since_last, Steps = 1):
    intervals = time_since_last

    ones_count = 0
    zeros_count = 0
    numbers = []
    # Iterate over the intervals in steps of 2
    for i in range(0, len(intervals) - 1, Steps):
        delta_t1 = intervals[i]
        delta_t2 = intervals[i + 1]

        if delta_t1 > delta_t2:
            numbers.append(1)
        elif delta_t1 < delta_t2:
            numbers.append(0)
        # If delta_t1 == delta_t2, we discard the event

    return numbers

def write_binary_to_file(binary_values, output_file_path):
    with open(output_file_path, 'w') as file:
        file.write("".join(map(str, binary_values)) + "\n")  # Writing all values on the same line

def main(input_file_path, output_file_path):
    # Step 1: Extract the last column values
    last_column_values = extract_last_column_values(input_file_path)

    # Step 2: Transform the values to binary
    binary_values = intervals_binary(last_column_values)

    # Step 3: Write the binary values to the output file
    write_binary_to_file(binary_values, output_file_path)

# Define file paths
input_file_path = 'Data/GeigerDataset_2024-05-11 09:18:27.155241.txt'
output_file_path = 'Data/Binary_Intervals.txt'

# Run the main function
main(input_file_path, output_file_path)
