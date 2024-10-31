import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient

# Set up Azure credentials
subscription_id='d03cbb48-56b4-43f6-8dbc-8e820f9fd0cb'
credential = DefaultAzureCredential()

# Initialize Compute and Resource Management clients
compute_client = ComputeManagementClient(credential, subscription_id)
resource_client = ResourceManagementClient(credential, subscription_id)

# Define your base Python script code
base_script = "./offchain-updater-coingecko.py"
# import os
# import sys

# # Your main Python script code goes here
# print(f"Hello from instance: {os.environ['INSTANCE_ID']}")
# """

def deploy_python_script(resource_group, location, instance_count, instance_configs):
    """
    Deploy multiple instances of a Python script to Azure, each with a slightly different configuration.
    
    Parameters:
    resource_group (str): The name of the Azure resource group to deploy to.
    location (str): The Azure region to deploy the instances in.
    instance_count (int): The number of instances to deploy.
    instance_configs (list[dict]): A list of dictionaries, where each dictionary represents the configuration for a single instance.
    The dictionaries should have keys matching the environment variables you want to set.
    """
    for i in range(instance_count):
        instance_id = f"instance-{i+1}"
        instance_config = instance_configs[i]

        # Create a virtual machine for the Python script
        vm_name = f"{instance_id}-vm"
        vm = compute_client.virtual_machines.create_or_update(
            resource_group_name=resource_group,
            vm_name=vm_name,
            parameters={
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
                }
            }
        )

        # Upload and run the Python script on the virtual machine
        vm.run_command(
            "RunShellScript",
            {
                "script": [
                    f"export INSTANCE_ID={instance_id}",
                    *[f"export {key}={value}" for key, value in instance_config.items()],
                    "python3 -c \"\"\"" + base_script + "\"\"\""
                ]
            }
        )

        print(f"Deployed instance {instance_id} with configuration: {instance_config}")

# Example usage
deploy_python_script(
    resource_group="my-resource-group",
    location="eastus",
    instance_count=5,
    instance_configs=[
        {"UPDATE_INTERVAL": "value1", "ENV_VAR2": "value2"},
        {"ENV_VAR1": "value3", "ENV_VAR2": "value4"},
        {"ENV_VAR1": "value5", "ENV_VAR2": "value6"}
    ]
)