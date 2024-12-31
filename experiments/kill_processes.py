import os
import signal

# Chat GPT

# Specify the file containing the PIDs
pid_file = "pids"

try:
    # Open the file and read PIDs
    with open(pid_file, "r") as file:
        pids = file.readlines()
    
    # Iterate through the PIDs and attempt to kill each
    for pid in pids:
        pid = pid.strip()  # Remove whitespace or newline
        if pid.isdigit():  # Ensure it's a valid number
            try:
                print(f"Killing process with PID: {pid}")
                os.kill(int(pid), signal.SIGTERM)  # Send SIGTERM to gracefully terminate
            except ProcessLookupError:
                print(f"Process with PID {pid} does not exist.")
            except PermissionError:
                print(f"Permission denied to kill process with PID {pid}.")
        else:
            print(f"Invalid PID: {pid}")
except FileNotFoundError:
    print(f"PID file '{pid_file}' not found.")
except Exception as e:
    print(f"An error occurred: {e}")
