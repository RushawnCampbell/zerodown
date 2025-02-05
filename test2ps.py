import paramiko
import subprocess
import os

def setup_ssh_on_remote(target_hostname, target_user, source_private_key_path, public_key_to_add):
    """Sets up SSH on a remote Windows machine using PowerShell, connecting passwordlessly.

    Args:
        target_hostname: The hostname or IP address of the remote machine.
        target_user: The username on the remote machine (needs initial password access).
        source_private_key_path: Path to the source machine's private key (for initial connection).
        public_key_to_add: The public key (as a string) that you want to add to authorized_keys.
    """

    try:
        # 1. Establish initial SSH connection (using password for the very first time)
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Handle host key verification carefully in production

        # Get the password from a secure source (e.g., environment variable)
        target_password = os.environ.get("TARGET_PASSWORD")
        if not target_password:
            raise ValueError("Target password not found in environment variable TARGET_PASSWORD")


        ssh_client.connect(hostname=target_hostname, username=target_user, password=target_password)

        # 2. Create .ssh directory on the target (if it doesn't exist)
        _execute_remote_powershell(ssh_client, "if (!(Test-Path -Path $HOME\\.ssh)) { New-Item -ItemType Directory -Path $HOME\\.ssh }")

        # 3. Set correct permissions on the .ssh directory
        _execute_remote_powershell(ssh_client, "icacls $HOME\\.ssh /grant \"$env:username:(OI)(CI)F\"")


        # 4. Create authorized_keys file (if it doesn't exist)
        _execute_remote_powershell(ssh_client, "if (!(Test-Path -Path $HOME\\.ssh\\authorized_keys)) { New-Item -ItemType File -Path $HOME\\.ssh\\authorized_keys }")

        # 5. Add the public key to authorized_keys
        _execute_remote_powershell(ssh_client, f"Add-Content -Path $HOME\\.ssh\\authorized_keys -Value '{public_key_to_add}'")

        # 6. Set correct permissions on authorized_keys
        _execute_remote_powershell(ssh_client, "icacls $HOME\\.ssh\\authorized_keys /grant \"$env:username:(OI)(CI)F\"")

        # 7. Disable password authentication (optional, but recommended for security)
        #  Edit the sshd_config file.  This is more complex and needs careful handling.
        #  A safer approach might be to leave password authentication enabled but rely on key-based auth.

        ssh_client.close()
        print("SSH setup complete.")

        # Now you can connect passwordlessly from the source machine:
        # ssh -i <source_private_key_path> <target_user>@<target_hostname>

    except Exception as e:
        print(f"Error setting up SSH: {e}")


def _execute_remote_powershell(ssh_client, powershell_command):
    """Executes a PowerShell command on the remote machine."""

    try:
        # Use Invoke-Expression for more complex commands. For simple commands, & might be enough.
        full_command = f"powershell.exe -Command \"Invoke-Expression '{powershell_command}'\""
        stdin, stdout, stderr = ssh_client.exec_command(full_command)
        exit_code = stdout.channel.recv_exit_status()

        if exit_code != 0:
            error_message = stderr.read().decode()
            raise Exception(f"PowerShell command failed: {error_message}")

        return stdout.read().decode()

    except Exception as e:
        raise Exception(f"Error executing remote command: {e}")



# Example usage (on the source machine):
if __name__ == "__main__":

    target_hostname = "your_target_hostname" # Replace with the target host
    target_user = "your_target_username" # Replace with the target user
    source_private_key_path = "~/.ssh/id_rsa"  # Replace with the path to your private key
    
    # 1. Generate a public key if you don't have one already:
    # ssh-keygen -t rsa  (and save it to a file, e.g., id_rsa_to_add)
    # 2. Read the public key:
    with open("id_rsa_to_add.pub", "r") as f:
        public_key_to_add = f.read().strip()

    setup_ssh_on_remote(target_hostname, target_user, source_private_key_path, public_key_to_add)