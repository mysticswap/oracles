import os
import time
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from datetime import datetime

def get_script_logs(compute_client, resource_group_name, vm_name):
    """Get logs from the running script using various methods"""
    try:
        # Method 1: Using journalctl to get Python script output
        poller = compute_client.virtual_machines.begin_run_command(
            resource_group_name,
            vm_name,
            {
                'command_id': 'RunShellScript',
                'script': [
                    'journalctl -u python3 -n 100 --no-pager',  # Last 100 lines
                    'tail -n 100 /var/log/syslog | grep python',  # System logs
                    'ps aux | grep python',  # Check if script is running
                ]
            }
        )
        result = poller.result()
        
        if result.value:
            for value in result.value:
                if value.message:
                    print(f"Log output: {value.message}")
        return result
    except Exception as e:
        print(f"Error getting logs: {str(e)}")
        return None

def monitor_script_logs(
    subscription_id,
    resource_group_name,
    vm_name,
    interval=60,  # Check every 60 seconds
    custom_log_file="/var/log/oracle_script.log"  # Custom log file path
):
    """Continuously monitor script logs"""
    
    # Create credential object
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, subscription_id)

    # First, set up logging on the VM with enhanced logging configuration
    setup_logging_commands = compute_client.virtual_machines.begin_run_command(
        resource_group_name,
        vm_name,
        {
            'command_id': 'RunShellScript',
            'script': [
                # Ensure log directory exists and has proper permissions
                'sudo mkdir -p /var/log/oracle',
                'sudo touch /var/log/oracle/script.log',
                'sudo chmod 666 /var/log/oracle/script.log',
                # Find Python processes and redirect their output
                'for pid in $(pgrep -f "python3"); do',
                '    sudo ls -l /proc/$pid/fd/1 2>/dev/null || true',
                '    sudo ls -l /proc/$pid/fd/2 2>/dev/null || true',
                '    sudo lsof -p $pid | grep -i python || true',
                'done',
                # Ensure Python processes output is captured
                'for pid in $(pgrep -f "python3"); do',
                f'    sudo bash -c "exec 1>/var/log/oracle/script.log exec 2>&1" || true',
                'done'
            ]
        }
    )
    setup_logging_commands.result()

    print(f"Starting log monitoring for VM: {vm_name}")
    print(f"Checking logs every {interval} seconds")
    print("Press Ctrl+C to stop monitoring")

    try:
        while True:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{current_time}] Fetching latest logs...")

            # Get logs using multiple methods to ensure we capture the output
            poller = compute_client.virtual_machines.begin_run_command(
                resource_group_name,
                vm_name,
                {
                    'command_id': 'RunShellScript',
                    'script': [
                        # Check Python process and its file descriptors
                        'echo "=== Python Processes ==="',
                        'ps aux | grep "python3" | grep -v grep',
                        'echo "\n=== Python Script Logs ==="',
                        'cat /var/log/oracle/script.log 2>/dev/null || echo "No logs found in script.log"',
                        'echo "\n=== System Logs with Python ==="',
                        'grep -i python /var/log/syslog | tail -n 20 || true',
                        'echo "\n=== Journalctl Logs ==="',
                        'journalctl -u python3 -n 20 --no-pager || true',
                        'echo "\n=== Resource Usage ==="',
                        'free -m',
                        'df -h',
                        'top -b -n 1 | head -n 20'
                    ]
                }
            )
            result = poller.result()

            if result.value:
                for value in result.value:
                    if value.message:
                        print(value.message)
                        
                        # Check for potential errors or warnings
                        if "error" in value.message.lower() or "exception" in value.message.lower():
                            print("\n⚠️  WARNING: Potential error detected in logs!")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nStopping log monitoring...")
    except Exception as e:
        print(f"An error occurred while monitoring: {str(e)}")

def get_script_status(compute_client, resource_group_name, vm_name):
    """Check if the script is currently running"""
    try:
        poller = compute_client.virtual_machines.begin_run_command(
            resource_group_name,
            vm_name,
            {
                'command_id': 'RunShellScript',
                'script': [
                    'ps aux | grep "python3" | grep -v grep',
                    'echo "\nScript Log Content:"',
                    'cat /var/log/oracle/script.log 2>/dev/null || echo "No logs found"'
                ]
            }
        )
        result = poller.result()
        
        if result.value and result.value[0].message:
            print("Script is running:")
            print(result.value[0].message)
            return True
        else:
            print("Script is not running!")
            return False
    except Exception as e:
        print(f"Error checking script status: {str(e)}")
        return False

if __name__ == "__main__":
    # Load environment variables
    subscription_id='d03cbb48-56b4-43f6-8dbc-8e820f9fd0cb'
    resource_group_name="MysticFinance_group"
    vm_name = "instance-1-vm"
    
    # Start monitoring
    monitor_script_logs(
        subscription_id,
        resource_group_name,
        vm_name,
        interval=60  # Check every 60 seconds
    )