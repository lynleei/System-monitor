# A little thing to check system status and health
#
# To use, first install the required libraries:
# pip install psutil
# To run the program:
# python stystem_monitor.py
#
# Author @ Lynlee Hong

import os
import platform
import socket
import subprocess
import sys
from datetime import datetime


# Attempt to import the psutil library, which provides system and process utilities.
try:
    import psutil
except ImportError:
    print("The 'psutil' library is not installed. Please install it using 'pip install psutil'.")
    sys.exit(1)

def get_system_info():
    """
    Fetch and return basic system information.

    Returns:
        dict: A dictionary containing information about the operating system, version, machine type,
              processor, and total RAM.
    """
    info = {
        "OS": f"{platform.system()} {platform.release()}",
        "Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "RAM": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB"
    }
    return info

def check_network():
    """
    Check network status and local IP with robust handling.

    Prints the hostname, local IP address, and internet connectivity status.
    """
    print("Network Status:")
    try:
        # Get the hostname and local IP address
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"Hostname: {hostname}")
        print(f"Local IP: {local_ip}")

        # Adjust ping command based on OS
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', '8.8.8.8']

        # Ping external site to check internet connectivity
        response = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if response.returncode == 0:
            print("Internet: Connected")
        else:
            print("Internet: Disconnected")
            print(f"Error: {response.stderr.decode().strip()}")
    except socket.gaierror as e:
        print(f"Could not get local IP: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    print()

def monitor_system_health():
    """
    Monitor and display system CPU, memory, and disk usage.

    Prints the current CPU usage percentage, memory usage percentage, and disk usage percentage.
    """
    print("System Health:")
    print(f"CPU Usage: {psutil.cpu_percent(interval=1)}%")
    print(f"Memory Usage: {psutil.virtual_memory().percent}%")
    print(f"Disk Usage: {psutil.disk_usage('/').percent}%")
    print()

if __name__ == "__main__":
    # Print a header for the system health monitor
    print("Production System Health Monitor")
    print("-" * 40)
    # Display the current date and time that the results were generated at
    print(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Retrieve and display system information
    system_info = get_system_info()
    print("System Information:")
    for key, value in system_info.items():
        print(f"{key}: {value}")
    print()
    
    # Check and display network status
    check_network()
    
    # Monitor and display system health metrics
    monitor_system_health()