import customtkinter as ctk
from tkinter import ttk
from PIL import Image, ImageTk
import tkinter as tk  # Import tkinter explicitly for BooleanVar
import os

class DriveExplorerCustomTkinter(ctk.CTk):
    def __init__(self, directory_lines, virtual_machines, applications):
        super().__init__()
        self.title("Drive, VM, and Application Explorer")
        self.geometry("900x450")  # Adjusted height for three columns and buttons

        self.directory_lines = directory_lines
        self.virtual_machines = virtual_machines
        self.applications = applications
        self.checkbox_vars = {}
        self.checked_items = {}  # Changed to a dictionary
        self.load_checkbox_images()
        self.create_three_column_layout()
        self.create_bottom_buttons()

    def load_checkbox_images(self):
        checked_image = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        for x in range(4, 12):
            for y in range(4, 12):
                checked_image.putpixel((x, y), (0, 0, 0, 255))

        unchecked_image = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        for x in range(4, 12):
            unchecked_image.putpixel((x, 4), (0, 0, 0, 255))
            unchecked_image.putpixel((x, 11), (0, 0, 0, 255))
            unchecked_image.putpixel((4, x), (0, 0, 0, 255))
            unchecked_image.putpixel((11, x), (0, 0, 0, 255))

        self.checked_image = ImageTk.PhotoImage(checked_image)
        self.unchecked_image = ImageTk.PhotoImage(unchecked_image)

    def create_three_column_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Column 1: Drive and Directory Tree
        self.drive_frame = ctk.CTkFrame(self)
        self.drive_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.drive_frame.grid_columnconfigure(0, weight=1)
        self.drive_frame.grid_rowconfigure(0, weight=1)

        self.drive_tree = ttk.Treeview(master=self.drive_frame, yscrollcommand=self.on_scrollbar_drive, show="tree headings")
        self.drive_tree.grid(row=0, column=0, sticky="nsew")

        self.drive_scrollbar = ctk.CTkScrollbar(master=self.drive_frame, orientation="vertical", command=self.drive_tree.yview)
        self.drive_scrollbar.grid(row=0, column=1, sticky="ns")

        self.drive_tree.configure(yscrollcommand=self.drive_scrollbar.set)
        self.drive_tree.heading("#0", text="Drives and Folders", anchor="w")
        self.build_drive_tree_from_lines()
        self.drive_tree.bind("<Button-1>", self.on_tree_click)
        self.drive_tree.bind("<Button-3>", self.on_right_click)

        # Column 2: Virtual Machines Tree
        self.vm_frame = ctk.CTkFrame(self)
        self.vm_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.vm_frame.grid_columnconfigure(0, weight=1)
        self.vm_frame.grid_rowconfigure(0, weight=1)

        self.vm_tree = ttk.Treeview(master=self.vm_frame, show="tree headings")
        self.vm_tree.grid(row=0, column=0, sticky="nsew")

        self.vm_scrollbar = ctk.CTkScrollbar(master=self.vm_frame, orientation="vertical", command=self.vm_tree.yview)
        self.vm_scrollbar.grid(row=0, column=1, sticky="ns")

        self.vm_tree.configure(yscrollcommand=self.vm_scrollbar.set)
        self.vm_tree.heading("#0", text="Virtual Machines", anchor="w")
        self.build_vm_tree()
        self.vm_tree.bind("<Button-1>", self.on_tree_click)
        self.vm_tree.bind("<Button-3>", self.on_right_click)

        # Column 3: Applications Tree
        self.app_frame = ctk.CTkFrame(self)
        self.app_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.app_frame.grid_columnconfigure(0, weight=1)
        self.app_frame.grid_rowconfigure(0, weight=1)

        self.app_tree = ttk.Treeview(master=self.app_frame, show="tree headings")
        self.app_tree.grid(row=0, column=0, sticky="nsew")

        self.app_scrollbar = ctk.CTkScrollbar(master=self.app_frame, orientation="vertical", command=self.app_tree.yview)
        self.app_scrollbar.grid(row=0, column=1, sticky="ns")

        self.app_tree.configure(yscrollcommand=self.app_scrollbar.set)
        self.app_tree.heading("#0", text="Applications", anchor="w")
        self.build_app_tree()
        self.app_tree.bind("<Button-1>", self.on_tree_click)
        self.app_tree.bind("<Button-3>", self.on_right_click)

    def create_bottom_buttons(self):
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        self.cancel_button = ctk.CTkButton(self.button_frame, text="Cancel Selection", command=self.cancel_selection)
        self.cancel_button.grid(row=0, column=0, padx=10, pady=5, sticky="ew") # Changed sticky to "ew"

        self.continue_button = ctk.CTkButton(self.button_frame, text="Continue", command=self.continue_selection)
        self.continue_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew") # Changed sticky to "ew"

        self.grid_rowconfigure(1, weight=0) # Ensure the button frame doesn't resize the window vertically

    def cancel_selection(self):
        print("Cancel button clicked. Clearing selections.")
        # Implement logic to clear all selections here
        for tree in [self.drive_tree, self.vm_tree, self.app_tree]:
            for item in tree.get_children():
                if item in self.checkbox_vars:
                    self.checkbox_vars[item].set(False)
                    tree.item(item, image=self.unchecked_image)
        self.checked_items = {}
        print(f"Checked Items after cancel: {self.checked_items}")

    def continue_selection(self):
        print("Continue button clicked.")
        print(f"Final checked items: {self.checked_items}")
        # Implement logic to proceed with the selected items here

    def on_scrollbar_drive(self, *args):
        self.drive_tree.yview(*args)

    def build_drive_tree_from_lines(self):
        tree_data = {}
        for line in self.directory_lines:
            parts = line.split("\\")
            drive = parts[0]
            if drive not in tree_data:
                tree_data[drive] = {}
            current_level = tree_data[drive]
            for part in parts[1:]:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]

        def insert_items(parent, data, path=""):
            for name, subdata in data.items():
                full_path = f"{path}\\{name}" if path else name
                item = self.drive_tree.insert(parent, "end", text=name, open=False, image=self.unchecked_image)
                self.checkbox_vars[item] = tk.BooleanVar(value=False)
                if subdata:
                    insert_items(item, subdata, full_path)

        for drive, data in tree_data.items():
            drive_item = self.drive_tree.insert("", "end", text=drive, open=False, image=self.unchecked_image)
            self.checkbox_vars[drive_item] = tk.BooleanVar(value=False)
            insert_items(drive_item, data)

    def build_vm_tree(self):
        root = self.vm_tree.insert("", "end", text="Virtual Machines", open=True)
        for vm in self.virtual_machines:
            item = self.vm_tree.insert(root, "end", text=vm, image=self.unchecked_image)
            self.checkbox_vars[item] = tk.BooleanVar(value=False)

    def build_app_tree(self):
        root = self.app_tree.insert("", "end", text="Applications", open=True)
        for app in self.applications:
            item = self.app_tree.insert(root, "end", text=app, image=self.unchecked_image)
            self.checkbox_vars[item] = tk.BooleanVar(value=False)

    def on_tree_click(self, event):
        tree = event.widget
        item = tree.identify_row(event.y)
        if item:
            self.toggle_checkbox(item, tree)

    def on_right_click(self, event):
        tree = event.widget
        item = tree.identify_row(event.y)
        if item:
            print(f"Right-clicked on item in {tree.winfo_name()}: {tree.item(item, 'text')}")

    def toggle_checkbox(self, item, tree):
        if item in self.checkbox_vars:
            current_state = self.checkbox_vars[item].get()
            self.checkbox_vars[item].set(not current_state)

            if self.checkbox_vars[item].get():
                tree.item(item, image=self.checked_image)
                item_text = tree.item(item, "text")
                parent = tree.parent(item)
                path_components = [item_text]
                while parent:
                    parent_text = tree.item(parent, "text")
                    path_components.insert(0, parent_text)
                    parent = tree.parent(parent)
                full_path = "\\".join(path_components)

                if tree == self.drive_tree:
                    drive = full_path.split("\\")[0]
                    if drive not in self.checked_items:
                        self.checked_items[drive] = set()
                    self.checked_items[drive].add(full_path)
                elif tree == self.vm_tree:
                    if "Virtual Machines" not in self.checked_items:
                        self.checked_items["Virtual Machines"] = set()
                    self.checked_items["Virtual Machines"].add(item_text)
                elif tree == self.app_tree:
                    if "Applications" not in self.checked_items:
                        self.checked_items["Applications"] = set()
                    self.checked_items["Applications"].add(item_text)

            else:
                tree.item(item, image=self.unchecked_image)
                item_text = tree.item(item, "text")
                parent = tree.parent(item)
                path_components = [item_text]
                while parent:
                    parent_text = tree.item(parent, "text")
                    path_components.insert(0, parent_text)
                    parent = tree.parent(parent)
                full_path = "\\".join(path_components)

                if tree == self.drive_tree:
                    drive = full_path.split("\\")[0]
                    if drive in self.checked_items and full_path in self.checked_items[drive]:
                        self.checked_items[drive].remove(full_path)
                        if not self.checked_items[drive]:
                            del self.checked_items[drive]
                elif tree == self.vm_tree:
                    if "Virtual Machines" in self.checked_items and item_text in self.checked_items["Virtual Machines"]:
                        self.checked_items["Virtual Machines"].remove(item_text)
                        if not self.checked_items["Virtual Machines"]:
                            del self.checked_items["Virtual Machines"]
                elif tree == self.app_tree:
                    if "Applications" in self.checked_items and item_text in self.checked_items["Applications"]:
                        self.checked_items["Applications"].remove(item_text)
                        if not self.checked_items["Applications"]:
                            del self.checked_items["Applications"]

            self.drive_tree.update_idletasks()
            self.vm_tree.update_idletasks()
            self.app_tree.update_idletasks()
            print(f"Item in {tree.winfo_name()}: {tree.item(item, 'text')}, Checked: {self.checkbox_vars[item].get()}")
            print(f"Checked Items: {self.checked_items}")

    def on_single_click(self, event):
        pass

if __name__ == "__main__":
    directory_lines = [
        "C:\\Folder1",
        "C:\\Folder1\\SubfolderA",
        "C:\\Folder1\\SubfolderA\\SubSubfolder1",
        "C:\\Folder1\\SubfolderB",
        "C:\\Folder2",
        "C:\\Folder2\\AnotherSubfolder",
        "D:\\AnotherDriveFolder",
        "D:\\AnotherDriveFolder\\SubDir",
        "C:\\VeryLongFolder1\\VeryLongSubfolderA\\VeryLongSubSubfolder1\\VeryLongSubSubSubfolderA\\VeryLongSubSubSubfolderB\\VeryLongSubSubSubfolderC",
        "C:\\VeryLongFolder1\\VeryLongSubfolderB\\VeryLongSubSubfolder2\\VeryLongSubSubSubfolderB",
        "D:\\AnotherVeryLongDriveFolder\\AnotherVeryLongSubDir\\AnotherVeryLongSubSubDir",
        "E:\\AnotherDriveFolder",
        "F:\\AnotherDriveFolder",
        "G:\\AnotherDriveFolder",
        "H:\\AnotherDriveFolder",
        "I:\\AnotherDriveFolder",
        "J:\\AnotherDriveFolder",
        "K:\\AnotherDriveFolder",
        "L:\\AnotherDriveFolder",
        "M:\\AnotherDriveFolder",
    ]

    virtual_machines = ["VM 1", "VM 2", "VM 3", "VM 4"]
    applications = ['APP ONE', 'APP TWO', 'APP THREE', 'APP FOUR']

    app = DriveExplorerCustomTkinter(directory_lines, virtual_machines, applications)
    app.mainloop()


    """import lz4.frame as lz4f
import io

def compress_data_stream(input_stream, output_filepath):
    try:
        with open(output_filepath, 'wb') as outfile:
            compressor = lz4f.create_compression_context()
            while True:
                chunk = input_stream.read(65536)  # Read chunks from the input stream
                if not chunk:
                    break
                compressed_chunk = lz4f.compress(chunk, compression_context=compressor)
                outfile.write(compressed_chunk)
            lz4f.flush(compressor, outfile) # Flush any remaining data
        print(f"Successfully compressed data stream to '{output_filepath}' using LZ4.")
    except Exception as e:
        print(f"An error occurred during stream compression: {e}")

if __name__ == "__main__":
    # Example: Reading data from a file-like object
    input_file = "your_large_file.bin"
    output_file = "compressed_stream.lz4"
    with open(input_file, 'rb') as infile:
        compress_data_stream(infile, output_file)"""
    
'''COMPRESS AND TRANSFERimport paramiko
import os
import lz4.frame
import time

def compress_and_transfer_file(hostname, port, username, password, remote_filepath, local_save_path):
    """
    Compresses a file on a remote Windows machine using LZ4 and transfers it
    to the local machine via SFTP using Paramiko.

    Args:
        hostname (str): The hostname or IP address of the remote Windows machine.
        port (int): The SSH port of the remote machine (usually 22).
        username (str): The username for SSH authentication.
        password (str): The password for SSH authentication.
        remote_filepath (str): The full path to the 100GB file on the remote machine.
        local_save_path (str): The local path where the compressed file will be saved.
    """
    try:
        # Establish SSH connection
        transport = paramiko.Transport((hostname, port))
        transport.connect(username=username, password=password)

        sftp = paramiko.SFTPClient.from_transport(transport)

        print(f"Connected to {hostname} via SSH and SFTP.")
        print(f"Attempting to compress and transfer: {remote_filepath}...")

        start_time = time.time()

        # Define the local filename for the compressed file
        remote_filename = os.path.basename(remote_filepath)
        compressed_filename = f"{remote_filename}.lz4"
        local_compressed_filepath = os.path.join(local_save_path, compressed_filename)

        print(f"Local save path: {local_compressed_filepath}")

        try:
            # Open the remote file for reading
            with sftp.open(remote_filepath, 'rb') as remote_file:
                # Open the local file for writing in binary mode
                with open(local_compressed_filepath, 'wb') as local_file:
                    print("Starting LZ4 compression and transfer...")
                    for chunk in iter(lambda: remote_file.read(1024 * 1024), b''):  # Read in 1MB chunks
                        compressed_chunk = lz4.frame.compress(chunk)
                        local_file.write(compressed_chunk)
                    print("File transfer and compression complete.")

            end_time = time.time()
            transfer_time = end_time - start_time
            print(f"Total time taken: {transfer_time:.2f} seconds.")

        except FileNotFoundError:
            print(f"Error: Remote file not found at {remote_filepath}")
        except Exception as e:
            print(f"An error occurred during transfer: {e}")

        # Close SFTP and SSH connection
        sftp.close()
        transport.close()
        print("SFTP and SSH connection closed.")

    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your username and password.")
    except paramiko.SSHException as e:
        print(f"Could not establish SSH connection: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Replace with your actual connection details and paths
    remote_host = "your_remote_host_ip_or_hostname"
    remote_port = 22  # Usually 22 for SSH
    remote_user = "your_remote_username"
    remote_password = "your_remote_password"
    remote_file = "C:\\path\\to\\your\\100gb\\file.dat"  # Example Windows path
    local_save_directory = "/path/to/your/local/directory"  # Example Linux/macOS path

    # Ensure the local save directory exists
    os.makedirs(local_save_directory, exist_ok=True)

    compress_and_transfer_file(remote_host, remote_port, remote_user, remote_password, remote_file, local_save_directory)

    print("\nRemember to replace the placeholder values in the script with your actual details.")
    print("Also, ensure you have the 'lz4' and 'paramiko' libraries installed on your local machine.")

'''

import paramiko

def get_windows_paths_and_vms(hostname, username, password):

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, username=username, password=password)

        # PowerShell command to get folder/subfolder paths and VM names
        powershell_command = """
            Get-PSDrive -DriveType 'Fixed' | ForEach-Object {
                Get-ChildItem -Path "$($_.Name):\" -Recurse -Directory -Force -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
            }
            Get-WmiObject -Class Win32_ComputerSystem | Select-Object -ExpandProperty Name
            Get-WmiObject -Class Win32_OperatingSystem | Select-Object -ExpandProperty Caption
            Get-WmiObject -Class Win32_Processor | Select-Object -ExpandProperty Name
            Get-WmiObject -Class Win32_PhysicalMemory | Select-Object -ExpandProperty Capacity
            Get-WmiObject -Class Win32_DiskDrive | Select-Object -ExpandProperty Model
            Get-WmiObject -Class Win32_NetworkAdapterConfiguration | Where-Object {$_.IPEnabled} | Select-Object -ExpandProperty IPAddress
            Get-WmiObject -Namespace root\\virtualization\\v2 -Class Msvm_ComputerSystem | Select-Object -ExpandProperty ElementName | ForEach-Object { "vm_detected_" + $_ }
        """

        stdin, stdout, stderr = client.exec_command(f'powershell -Command "{powershell_command}"')
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()

        client.close()

        if error:
            print(f"Error executing command: {error}")
            return []
        else:
            return output.split('\n')

    except paramiko.AuthenticationException:
        print("Authentication failed.")
        return []
    except paramiko.SSHException as e:
        print(f"Could not establish SSH connection: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

if __name__ == "__main__":
    # Replace with your Windows machine details
    remote_host = "your_windows_ip_or_hostname"
    remote_user = "your_username"
    remote_password = "your_password"

    results = get_windows_paths_and_vms(remote_host, remote_user, remote_password)

    if results:
        for item in results:
            print(item)



def get_windows_volumes(hostname, username, port=22, key_filename=None):
        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.RejectPolicy())


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

    #HELPER METHODS
 #command = 'Get-WmiObject Win32_Volume | ForEach-Object {$DriveLetter=$_.DriveLetter; if ($DriveLetter) {Get-ChildItem -Path "$DriveLetter\" -Directory -Recurse -Force | Select-Object -ExpandProperty FullName | ForEach-Object {"$DriveLetter" + [char]9 + $_}}} | Out-String -Stream | ForEach-Object {$_.TrimEnd()}'
                    #command= 'Get-WmiObject Win32_Volume | ForEach-Object {$DriveLetter=$_.DriveLetter; if ($DriveLetter) {Get-ChildItem -Path "$DriveLetter\" -Directory -Recurse -Force | Select-Object -ExpandProperty FullName | ForEach-Object {$DriveLetter + $_}}} | Out-String -Stream | ForEach-Object {$_.TrimEnd()}'
    