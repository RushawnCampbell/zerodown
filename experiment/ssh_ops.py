import paramiko
import json
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_windows_volumes(hostname, username, port=22, key_filename=None):
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #client.set_missing_host_key_policy(paramiko.RejectPolicy())    will be used for subsequent connection

       
        logging.info(f"Using key file: {key_filename}")
        key = paramiko.RSAKey.from_private_key_file(key_filename)
        client.connect(hostname=hostname, username=username, port=port, pkey=key)

        command="powershell.exe -command \" Get-WmiObject Win32_Volume | Select-Object DriveLetter, Capacity, FreeSpace | ConvertTo-Json\""
        _, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()

        if error:
            logging.error(f"Error executing command: {error}")
            return None

        try:
            volume_data = [json.loads(output)]
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON: {e}. Output: {output}")
            return None

        volumes = {}
        for volume in volume_data:
            drive_letter = volume.get('DriveLetter')
            if drive_letter:
                total_space = int(volume.get('Capacity', 0))
                free_space = int(volume.get('FreeSpace', 0))
                volumes[drive_letter] = {"total": total_space, "free": free_space}
        return volumes

    except paramiko.AuthenticationException:
        logging.error("Authentication failed.")
        return None
    except paramiko.SSHException as e:
        logging.error(f"SSH connection failed: {e}")
        return None
    except Exception as e:
        logging.exception("An unexpected error occurred:")
        return None
    finally:
        if 'client' in locals() and client:
            client.close()

if __name__ == "__main__":
    hostname = "3.144.219.127"  #18.117.188.132
    username = "Administrator"  
    key_filename = os.path.join(os.path.expanduser("~"), ".ssh", "id_rsa")

    volumes = get_windows_volumes(hostname, username, key_filename=key_filename)

    if volumes:
        logging.info("Volume Information:")
        for volume, space in volumes.items():
            total_gb = space["total"] / (1024 ** 3)
            free_gb = space["free"] / (1024 ** 3)
            logging.info(f"\nDrive: {volume} \nTotal: {total_gb:.2f} GB \nFree: {free_gb:.2f} GB")
    else:
        logging.error("Failed to retrieve volume information.")