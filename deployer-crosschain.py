import os
import time
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import AzureError


# Set up Azure credentials
subscription_id='d03cbb48-56b4-43f6-8dbc-8e820f9fd0cb'
credential = DefaultAzureCredential()

# Initialize Compute and Resource Management clients
compute_client = ComputeManagementClient(credential, subscription_id)
network_client = NetworkManagementClient(credential, subscription_id)
resource_client = ResourceManagementClient(credential, subscription_id)

# Define your base Python script code
base_script = "./offchain-crosschain-updated.py"
# import os
# import sys

# # Your main Python script code goes here
# print(f"Hello from instance: {os.environ['INSTANCE_ID']}")
# """

def wait_for_vm_ready(compute_client, resource_group_name, vm_name, timeout=300):
    """Wait for VM to be ready for commands"""
    start_time = time.time()
    while True:
        vm_status = compute_client.virtual_machines.instance_view(resource_group_name, vm_name).statuses
        vm_power_state = [status for status in vm_status if status.code.startswith('PowerState/')][0]
        if vm_power_state.code == 'PowerState/running':
            print('running')
            return True
        if time.time() - start_time > timeout:
            raise TimeoutError("VM failed to reach ready state within timeout period")
        time.sleep(10)

def run_command_on_vm(compute_client, resource_group_name, vm_name, instance_id, instance_config, base_script):
    """Execute specific command on the VM"""
    try:
        print(f"Running script on VM for instance {instance_id}")
        # Create environment variables export commands
        env_exports = '\n'.join([f"export {key}='{value}'" for key, value in instance_config.items()])
        env_exports = f"export INSTANCE_ID='{instance_id}'\n{env_exports}"
        
        # Commands to set up and run the script
        commands = [
            # Create directory
            "mkdir -p ~/scripts",
            
            # Save environment variables and script
            f"echo '{env_exports}' > ~/scripts/env.sh",
            f"echo '{base_script}' > ~/scripts/oracle.py",
            
            # Set proper permissions
            "chmod +x ~/scripts/env.sh",
            "chmod +x ~/scripts/oracle.py",
            
            # Update package lists and install system dependencies
            "sudo apt-get update",
            "sudo apt-get install -y python3-pip python3-dev build-essential",
            
            # Upgrade pip and install required packages
            "sudo pip3 install --upgrade pip",
            "sudo pip3 install web3 python-dotenv requests eth_account eth_keys eth_utils eth_typing eth_abi eth_hash[pycryptodome]",
            
            # Run the script with environment variables and logging
            "source ~/scripts/env.sh && python3 ~/scripts/oracle.py > ~/scripts/output.log 2>&1 &",
            "echo 'Script started in background. Check output.log for details.'",
            
            # Show the running processes and initial log output
            "ps aux | grep python",
            "tail -f ~/scripts/output.log &"
        ]
        print(commands)
        poller = compute_client.virtual_machines.begin_run_command(
            resource_group_name,
            vm_name,
            {
                'command_id': 'RunShellScript',
                'script': commands
            }
        )
        result = poller.result()
        print("Command execution result:")
        if result.value:
            for value in result.value:
                print(f"stdout: {value.message}")
        return result
    except Exception as e:
        print(f"Error running command: {str(e)}")
        raise



def deploy_python_script(resource_group, location, instance_count, instance_configs, skip_deployment=False):
  try:
    """
    Deploy multiple instances of a Python script to Azure, each with a slightly different configuration.
    
    Parameters:
    resource_group (str): The name of the Azure resource group to deploy to.
    location (str): The Azure region to deploy the instances in.
    instance_count (int): The number of instances to deploy.
    instance_configs (list[dict]): A list of dictionaries, where each dictionary represents the configuration for a single instance.
    The dictionaries should have keys matching the environment variables you want to set.
    """
   
    # Create or check resource group
    resource_client.resource_groups.create_or_update(
        resource_group,
        {"location": location}
    )

    for i in range(instance_count):
        instance_id = f"instance-{i+1}"
        instance_config = instance_configs[i]

        # Create a virtual machine for the Python script
        vm_name = f"{instance_id}-vm"
        vnet_name = f"{vm_name}-vnet"
        if not skip_deployment:
            
            poller = network_client.virtual_networks.begin_create_or_update(
                resource_group,
                vnet_name,
                {
                    "location": location,
                    "address_space": {
                        "address_prefixes": ["10.0.0.0/16"]
                    }
                }
            )
            vnet_result = poller.result()

            # Create Subnet
            subnet_name = f"{vm_name}-subnet"
            poller = network_client.subnets.begin_create_or_update(
                resource_group,
                vnet_name,
                subnet_name,
                {"address_prefix": "10.0.0.0/24"}
            )
            subnet_result = poller.result()

            # Create Public IP
            public_ip_name = f"{vm_name}-ip"
            poller = network_client.public_ip_addresses.begin_create_or_update(
                resource_group,
                public_ip_name,
                {
                    "location": location,
                    "sku": {"name": "Standard"},
                    "public_ip_allocation_method": "Static",
                    "public_ip_address_version": "IPV4"
                }
            )
            ip_address_result = poller.result()

            # Create NIC
            nic_name = f"{vm_name}-nic"
            poller = network_client.network_interfaces.begin_create_or_update(
                resource_group,
                nic_name,
                {
                    "location": location,
                    "ip_configurations": [{
                        "name": f"{vm_name}-ipconfig",
                        "subnet": {"id": subnet_result.id},
                        "public_ip_address": {"id": ip_address_result.id}
                    }]
                }
            )
            nic_result = poller.result()
            vm = compute_client.virtual_machines.begin_create_or_update(
                resource_group,
                vm_name,
                {
                    "location": location,
                    "os_profile": {
                        "computer_name": vm_name,
                        "admin_username": "azureuser",
                        "admin_password": "P@ssw0rd1234!"
                    },
                    "hardware_profile": {
                        "vm_size": "Standard_B1s"
                    },
                    "storage_profile": {
                        "image_reference": {
                            "publisher": "Canonical",
                            "offer": "UbuntuServer",
                            "sku": "18.04-LTS",
                            "version": "latest"
                        }
                    },
                    "network_profile": {
                        "network_interfaces": [{
                            "id": nic_result.id,
                        }]
                    }
                }
            )

            # Upload and run the Python script on the virtual machine
            vm_result = vm.result()

            print(f"Provisioned virtual machine {vm_name}")
        
            # Wait for VM to be ready
            print("Waiting for VM to be ready...")
            wait_for_vm_ready(compute_client, resource_group, vm_name)

            # Install Python and required packages
            setup_commands = compute_client.virtual_machines.begin_run_command(
                resource_group,
                vm_name,
                {
                    'command_id': 'RunShellScript',
                    'script': [
                        "sudo apt-get update",
                        "sudo apt-get install -y python3-pip",
                        "sudo pip3 install web3 python-dotenv requests"
                    ]
                }
            )
            setup_commands.result()
        
        run_command_on_vm(compute_client, resource_group, vm_name, instance_id, instance_config, base_script)
        

        print(f"Deployed instance {instance_id}")
  except AzureError as e:
        print(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    # Your Python script as a string
    with open("./offchain-crosschain-updated.py", "r") as file:
        base_script = file.read()
        
    # Example usage
    deploy_python_script(
        resource_group="MysticFinance_group",
        location="westus2",
        instance_count=1,
        instance_configs=[
            {"UPDATE_INTERVAL": "21600", "SOURCE_ORACLE_ADDRESS": "0xF4E1B57FB228879D057ac5AE33973e8C53e4A0e0", "TARGET_ORACLE_ADDRESS":"0x583B9627ffb06dd5923315C3B62330Bd59E41946", "SOURCE_RPC_URL":"https://eth.llamarpc.com", "TARGET_RPC_URL":"https://test-rpc.plumenetwork.xyz", "PRIVATE_KEY":"0x3a420ce820887aa58ae6e88452d7000d2aedaebd3b94910108a73ad1e323f4d7"},
            # {"ENV_VAR1": "value3", "ENV_VAR2": "value4"},
            # {"ENV_VAR1": "value5", "ENV_VAR2": "value6"}
        ],
        skip_deployment=False
    )