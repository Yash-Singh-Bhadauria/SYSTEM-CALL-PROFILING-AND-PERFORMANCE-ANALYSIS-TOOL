import os
import subprocess
import re
import time
from collections import defaultdict


def parse_strace_output(output):
    """
    Parses the output from strace and collects syscall statistics.
    """
    syscall_data = defaultdict(int)
    failed_syscalls = defaultdict(int)
    total_time = defaultdict(float)

    for line in output.splitlines():
        # Regex to match syscall lines like: write(1, "Hello\n", 6) = 6 <0.000005>
        match = re.match(r'(\w+)\((.*?)\)\s+=\s+(-?\d+|\?)\s*<([\d.]+)?>', line)
        if match:
            syscall_name = match.group(1)
            return_value = match.group(3)
            time_spent = match.group(4)

            # Increment syscall count
            syscall_data[syscall_name] += 1

            # If time is present, accumulate it
            if time_spent:
                total_time[syscall_name] += float(time_spent)

            # Check for failed syscalls (negative return value)
            if return_value.startswith('-'):
                failed_syscalls[syscall_name] += 1

    return syscall_data, failed_syscalls, total_time


def write_to_file(file_name, syscall_data, failed_syscalls, total_time):
    """
    Writes system call statistics to a text file.
    """
    try:
        with open(file_name, 'w') as file:
            file.write("System Call Summary:\n")
            for syscall, count in syscall_data.items():
                file.write(f"{syscall}: {count} calls, {total_time[syscall]:.6f} s\n")

            if failed_syscalls:
                file.write("\nFailed System Calls:\n")
                for syscall, count in failed_syscalls.items():
                    file.write(f"{syscall}: {count} failures\n")

        print(f"System call summary saved to {file_name}")
    except Exception as e:
        print(f"Error writing to file: {e}")


def trace_program(program, output_file):
    """
    Uses strace to trace a program and analyze its system calls.
    """
    try:
        print(f"Tracing program: {program}")
        # Start strace process
        process = subprocess.Popen(
            ['strace', '-T', '-e', 'trace=all', program],
            stderr=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            text=True
        )

        print("Running the program...")
        _, stderr_output = process.communicate()

        print("Parsing system call data...")
        syscall_data, failed_syscalls, total_time = parse_strace_output(stderr_output)

        print("\nSystem Call Summary:")
        for syscall, count in syscall_data.items():
            print(f"{syscall}: {count} calls, {total_time[syscall]:.6f} s")

        if failed_syscalls:
            print("\nFailed System Calls:")
            for syscall, count in failed_syscalls.items():
                print(f"{syscall}: {count} failures")

        # Write output to file
        write_to_file(output_file, syscall_data, failed_syscalls, total_time)

    except FileNotFoundError:
        print("Error: 'strace' command not found. Please install strace.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    program = input("Enter the program or script to trace (e.g., './example_program'): ")
    if os.path.exists(program):
        output_file = input("Enter the name of the output file (e.g., 'output.txt'): ")
        trace_program(program, output_file)
    else:
        print("Error: Program not found.")
