import os
import paramiko
import subprocess
import sys
import logging
import time

class ZeroStorageNode():

    def __init__(self):
        self.key_path = os.path.join(os.path.expanduser("~"), ".ssh", "zero_id_rsa")
        self.key = ''
        self.exec_policy = ''
        self.logger = logging.getLogger(__name__)

    def get_exec_policy(self):
        try:
            result = subprocess.run(["powershell.exe", "-Command", "Get-ExecutionPolicy"], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error getting execution policy: {e}")
            return None

    def set_exec_policy(self, policy):
        try:
            subprocess.run(["powershell.exe", "-Command", f"Set-ExecutionPolicy {policy} -Force"], check=True)
            self.logger.info(f"Execution policy set to {policy}.")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error setting execution policy: {e}")
            sys.exit(1)

    def is_admin(self):
        try:
            return os.getuid() == 0
        except AttributeError:
            try:
                subprocess.run(["net", "session"], capture_output=True, check=True)
                return True
            except subprocess.CalledProcessError:
                return False

    def open_firewall_port(self, port=22, protocol="TCP", rule_name="ALLOW SSH"):
        if not self.is_admin():
            self.logger.error("This script must be run with administrator privileges.")
            sys.exit(1)

        try:
            subprocess.run([
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name={rule_name}", "dir=in", f"localport={port}",
                f"protocol={protocol}", "action=allow"
            ], check=True)
            self.logger.info(f"Firewall rule '{rule_name}' added for port {port} ({protocol}).")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error opening firewall port: {e}")
            sys.exit(1)

    def install_openssh_server(self):
        try:
            check_installed = subprocess.run(["powershell.exe", "-Command", "Get-WindowsCapability -Online | ? Name -like 'OpenSSH.Server*'"], capture_output=True, text=True, check=False)

            if "Installed" not in check_installed.stdout:
                install_command = "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0"
                subprocess.run(["powershell.exe", "-Command", install_command], check=True)
                self.logger.info("OpenSSH Server feature installed.")
            else:
                self.logger.info("OpenSSH Server is already installed. Skipping installation.")

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error installing OpenSSH Server: {e}")
            sys.exit(1)

    def start_ssh_service(self):
        try:
            check_service = subprocess.run(["powershell.exe", "-Command", "Get-Service sshd"], capture_output=True, text=True, check=False)
            if "sshd" in check_service.stdout:
                subprocess.run(["powershell.exe", "-Command", "Start-Service sshd"], check=True)
                self.logger.info("SSH service started.")

                subprocess.run(["powershell.exe", "-Command", "Set-Service -Name sshd -StartupType Automatic"], check=True)
                self.logger.info("SSH service startup set to automatic.")
            else:
                self.logger.error("SSH service not found. Installation may have failed.")
                sys.exit(1)

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error starting SSH service or setting startup type: {e}")
            sys.exit(1)

    def keys_generator(self):
        try:
            keys_dir = os.path.dirname(self.key_path)
            if not os.path.exists(keys_dir):
                os.makedirs(keys_dir)
                self.logger.info(f"Created directory: {keys_dir}")

            if os.path.exists(self.key_path) or os.path.exists(self.key_path + ".pub"):
                self.logger.info(f"Key pair already exists at {self.key_path}. Skipping generation.")
                return -1

            self.key = paramiko.RSAKey.generate(4096)

            self.key.write_private_key_file(self.key_path)
            self.logger.info(f"Private key saved to {self.key_path}")

            pub_key = self.key.get_name() + " " + self.key.get_base64()
            with open(self.key_path + ".pub", "w") as f:
                f.write(pub_key)
            self.logger.info(f"Public key saved to {self.key_path}.pub")

        except Exception as e:
            self.logger.error(f"Error generating keys: {e}")

    def append_pub_key():
        pub_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC/MrB32eP7QhkbOxRiKjtTU5Egn93j57RdNM7WtZowgFno0FzQLHm6r+UFDce+QJPmaUZLtbDk4JbKDXhxSULkR9xK2XEVJ2hIXgMII7qKLB0FodKHf2kF9pw9jofPkhLzE6C6wYAVgZs5r82NQZ4jeorhDJtCAbNcekuobt9FK6cU2ExFbSZH9HzlpGMQsFZ6AssX6YAdaeJwiWgnIbk0VVEq+H8SSobyScruAGhOJ0Vq2kDL7INn/Zr3wmSa52OLlskhoYGKJ8IIoYy8e6yGEQqGLpixi2jKvTuMXXXiOwzLvFqIEVhAW8en+4Q0jRbpFZ6zKXyngO8Y33WS56YeHzJ1KoO6ZcYwrzbUgNM9Twgweb0pvqLp1IAcwo8D8UxqHOsLNAwqrKpWqGUD0/ZbT4drSsvduVgkVWMmWaWubweDiocAzZUYRa/qEFWidiOTOhM4x6fp0/tS/JFIaLYJSWvrNYIeg1kP3X2oVOyjetAI8adqq/0+X0PApN4yqBnfGJku2H9nCDC5yl/frRGlsf3KNNeM2rEtSk7j+A7M2UCnocK3KEqNieJ7C2FRW6NomdYzcDru7w9maSqYk+M7dmzInrgAYc8F6SG0VvV6H+EsgpMUnjX/A4aqVl6Jh5Ky7f0nDzbjRE9miAha88Lye403zPwQp2PUoUj7KiV7aQ=="
        subprocess.run(["powershell.exe", "-Command", f'{pub_key} | Out-File -FilePath "$env:USERPROFILE\.ssh\authorized_keys" -Append'], capture_output=True, text=True, check=False)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S') #Added datefmt
    zerostoragenode = ZeroStorageNode()
    zerostoragenode.exec_policy = zerostoragenode.get_exec_policy()
    if zerostoragenode.exec_policy != "RemoteSigned":
        zerostoragenode.set_exec_policy("RemoteSigned")
    zerostoragenode.logger.info("Creating Firewall Rules")
    zerostoragenode.open_firewall_port()
    zerostoragenode.logger.info("Installing OpenSSH Server")
    zerostoragenode.install_openssh_server()
    zerostoragenode.logger.info("Generating Keys")
    zerostoragenode.keys_generator()
    zerostoragenode.logger.info("Configuring SSH service")
    zerostoragenode.start_ssh_service()
    zerostoragenode.append_pub_key()
    zerostoragenode.logger.info("Authorized Key Updated")
    zerostoragenode.logger.info("This Window will be closed in 20 seconds")
    time.sleep(20)