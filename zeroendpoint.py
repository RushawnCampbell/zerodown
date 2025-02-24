import os
import paramiko, time, subprocess,sys

class ZeroEndpoint():

    def __init__(self):
        self.key_path= os.path.join(os.path.expanduser("~"), ".ssh", "zero_endpoint") 
        self.key=''
        self.exec_policy=''

    #Gets the current PowerShell execution policy.
    def get_exec_policy(self):
        try:
            result = subprocess.run(["powershell.exe", "-Command", "Get-ExecutionPolicy"], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error getting execution policy: {e}", file=sys.stderr)  # Print to stderr for errors
            return None
    
    #Sets Execution Policy
    def set_exec_policy(self,policy):
        """Sets the PowerShell execution policy."""
        try:
            subprocess.run(["powershell.exe", "-Command", f"Set-ExecutionPolicy {policy} -Force"], check=True)
            print(f"Execution policy set to {policy}.")
        except subprocess.CalledProcessError as e:
            print(f"Error setting execution policy: {e}", file=sys.stderr)
            sys.exit(1)  # Exit with error code
    
    #Checks if script is executed as Administrator
    def is_admin(self):
        try:
            return os.getuid() == 0 # Check for root/admin privileges (Unix-like systems)
        except AttributeError: # For Windows systems
            try:
                subprocess.run(["net", "session"], capture_output=True, check=True) # Try to run a command that requires admin
                return True
            except subprocess.CalledProcessError:
                return False

    #Creates Windows Firewall rule for ssh
    def open_firewall_port(self, port=22, protocol="TCP", rule_name="ALLOW SSH"):
        
        if not self.is_admin():
            print("This script must be run with administrator privileges.")
            sys.exit(1)

        try:
            subprocess.run([
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name={rule_name}", "dir=in", f"localport={port}",
                f"protocol={protocol}", "action=allow"
            ], check=True)
            print(f"Firewall rule '{rule_name}' added for port {port} ({protocol}).")
        except subprocess.CalledProcessError as e:
            print(f"Error opening firewall port: {e}")
            sys.exit(1)

    def install_openssh_server(self):
        try:
            # Checks if OpenSSH Server is installed and avoids reinstallation
            check_installed = subprocess.run(["powershell.exe", "-Command", "Get-WindowsCapability -Online | ? Name -like 'OpenSSH.Server*'"], capture_output=True, text=True, check=False)

            if "Installed" not in check_installed.stdout:
                #Using Windows Optional Feature for installation 
                install_command = "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0" 
                subprocess.run(["powershell.exe", "-Command", install_command], check=True)
                print("OpenSSH Server feature installed.")

            else:
                print("OpenSSH Server is already installed. Skipping installation.")

        except subprocess.CalledProcessError as e:
            print(f"Error installing OpenSSH Server: {e}")
            sys.exit(1)

    #Starts the SSH service and sets its startup type to automatic.
    def start_ssh_service(self):
        try:
            # Checking if the service exists
            check_service = subprocess.run(["powershell.exe", "-Command", "Get-Service sshd"], capture_output=True, text=True, check=False)
            if "sshd" in check_service.stdout:
                subprocess.run(["powershell.exe", "-Command", "Start-Service sshd"], check=True)
                print("SSH service started.")

                subprocess.run(["powershell.exe", "-Command", "Set-Service -Name sshd -StartupType Automatic"], check=True)
                print("SSH service startup set to automatic.")
            else:
                print("SSH service not found.  Installation may have failed.")
                sys.exit(1) # Exit with error

        except subprocess.CalledProcessError as e:
            print(f"Error starting SSH service or setting startup type: {e}")
            sys.exit(1)
    
    #Generates SSH key pairs 
    def keys_generator(self):
       try:
           keys_dir = os.path.dirname(self.key_path)
           if not os.path.exists(keys_dir):
               os.makedirs(keys_dir)
               print(f"Created directory: {keys_dir}")
               time.sleep(5)

           if os.path.exists(self.key_path) or os.path.exists(self.key_path + ".pub"):
               print(f"Key pair already exists at {self.key_path}. Skipping generation.")
               time.sleep(5)
               return -1

           self.key = paramiko.RSAKey.generate(4096) 

           # Saving private key
           self.key.write_private_key_file(self.key_path)
           print(f"Private key saved to {self.key_path}")

           # Saving public key
           pub_key = self.key.get_name() + " " + self.key.get_base64()
           with open(self.key_path + ".pub", "w") as f:
               f.write(pub_key)
           print(f"Public key saved to {self.key_path}.pub")
           time.sleep(15)

       except Exception as e:
           print(f"Error generating keys: {e}")
           time.sleep(15)


if __name__ == "__main__":

    zeroendpoint = ZeroEndpoint()
    zeroendpoint.exec_policy = zeroendpoint.get_exec_policy()
    if zeroendpoint.exec_policy != "RemoteSigned":
        zeroendpoint.set_exec_policy("RemoteSigned")
    print("Creating Firewall Rules")
    zeroendpoint.open_firewall_port()
    print("Install OpenSSH Server")
    zeroendpoint.install_openssh_server()
    print("Generating Keys")
    zeroendpoint.keys_generator()
    print("Configuring SSH service")
    zeroendpoint.start_ssh_service()
    zeroendpoint.set_exec_policy(zeroendpoint.exec_policy)
    print("This Window will be closed in 20 seconds")
    time.sleep(20)

    


