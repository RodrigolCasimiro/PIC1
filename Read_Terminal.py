import serial

# Setup the serial connection
Uno = serial.Serial("/dev/cu.usbmodem1101", 9600)

# Open (or create if doesn't exist) the file to save the data
with open("geiger_data.txt", "a") as file:
    while True:
        try:
            # Read a line from the Arduino
            line = Uno.readline().decode("utf-8").rstrip()
            # Save the line to the file
            file.write(line + "\n")
            file.flush()
        except KeyboardInterrupt:
            print("Stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue
