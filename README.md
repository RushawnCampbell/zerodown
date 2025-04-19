# zerodown
ZeroDown Project for capstone
from frontend.components.Popup import Popup
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import customtkinter as gui
from flask import jsonify
import requests

class RemoteExplorer(Popup):
    def __init__(self, master, title, endpoint_name):
        super().__init__(master, title)
        self.master = master
        self.endpoint_name = endpoint_name
        self.configure(fg_color="#2B2B2B")
        self.after(500, self.custom_set_pos)
        self.checkbox_vars = {}
        self.checked_items = {}
        self.load_checkbox_images()
        self.create_three_column_layout()
        self.create_bottom_buttons()

    def custom_set_pos(self):
        self.set_window_position(900, 450)

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

        # Column 1: Volume Tree
        self.vol_frame = gui.CTkFrame(self)
        self.vol_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew") # Changed column to 0
        self.vol_frame.grid_columnconfigure(0, weight=1)
        self.vol_frame.grid_rowconfigure(0, weight=1)

        self.vol_tree = ttk.Treeview(master=self.vol_frame, show="tree headings")
        self.vol_tree.grid(row=0, column=0, sticky="nsew")

        self.vol_scrollbar = gui.CTkScrollbar(master=self.vol_frame, orientation="vertical", command=self.vol_tree.yview)
        self.vol_scrollbar.grid(row=0, column=1, sticky="ns")

        self.vol_tree.configure(yscrollcommand=self.vol_scrollbar.set)
        self.vol_tree.heading("#0", text="Volumes", anchor="w")
        self.build_vol_tree()
        self.vol_tree.bind("<Button-1>", self.on_tree_click)

        # Column 2: Virtual Machines Tree
        self.vm_frame = gui.CTkFrame(self)
        self.vm_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew") # Changed column to 1
        self.vm_frame.grid_columnconfigure(0, weight=1)
        self.vm_frame.grid_rowconfigure(0, weight=1)

        self.vm_tree = ttk.Treeview(master=self.vm_frame, show="tree headings")
        self.vm_tree.grid(row=0, column=0, sticky="nsew")

        self.vm_scrollbar = gui.CTkScrollbar(master=self.vm_frame, orientation="vertical", command=self.vm_tree.yview)
        self.vm_scrollbar.grid(row=0, column=1, sticky="ns")

        self.vm_tree.configure(yscrollcommand=self.vm_scrollbar.set)
        self.vm_tree.heading("#0", text="Virtual Machines", anchor="w")
        self.build_vm_tree()
        self.vm_tree.bind("<Button-1>", self.on_tree_click)

        # Column 3: Applications Tree
        self.app_frame = gui.CTkFrame(self)
        self.app_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew") # Changed column to 2
        self.app_frame.grid_columnconfigure(0, weight=1)
        self.app_frame.grid_rowconfigure(0, weight=1)

        self.app_tree = ttk.Treeview(master=self.app_frame, show="tree headings")
        self.app_tree.grid(row=0, column=0, sticky="nsew")

        self.app_scrollbar = gui.CTkScrollbar(master=self.app_frame, orientation="vertical", command=self.app_tree.yview)
        self.app_scrollbar.grid(row=0, column=1, sticky="ns")

        self.app_tree.configure(yscrollcommand=self.app_scrollbar.set)
        self.app_tree.heading("#0", text="Applications", anchor="w")
        self.build_app_tree()
        self.app_tree.bind("<Button-1>", self.on_tree_click)

    def create_bottom_buttons(self):
        self.button_frame = gui.CTkFrame(self)
        self.button_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        self.cancel_button = gui.CTkButton(self.button_frame, text="Cancel Selection", command=self.cancel_selection)
        self.cancel_button.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.continue_button = gui.CTkButton(self.button_frame, text="Continue", command=self.continue_selection)
        self.continue_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        self.grid_rowconfigure(1, weight=0)

    def cancel_selection(self):
        self.master.volumes = []
        #self.master.virtual_machines = ["VM 1", "VM 2", "VM 3", "VM 4"]
        #self.master.applications = ['APP ONE', 'APP TWO', 'APP THREE', 'APP FOUR']
        self.on_close()

    def continue_selection(self):
        #self.master.volumes = self.checked_items
        for drive,size in self.checked_items['Volumes'].items():
            print("DRIVE", drive, "SIZE", size)
            self.master.backup_demand += size
        print("DEMAND IS", self.master.backup_demand)
        #self.master.browse_destination_button.configure(state='normal', fg_color="#1F6AA5")
        self.master.storage_node_dropdown.configure(state="normal", fg_color= "#FFF", border_color="#FFF",  dropdown_fg_color="#FFFFFF", dropdown_text_color="#000000")
        self.master.volumes = []
        #self.master.virtual_machines = ["VM 1", "VM 2", "VM 3", "VM 4"]
        #self.master.applications = ['APP ONE', 'APP TWO', 'APP THREE', 'APP FOUR']
        self.on_close()

    def on_scrollbar_drive(self, *args):
        pass # Removed as it seems unused in the current context

    def build_vol_tree(self):
        root = self.vol_tree.insert("", "end", text="Volumes", open=True)
        if hasattr(self.master, 'volumes') and self.master.volumes:
            for vol in self.master.volumes:
                item = self.vol_tree.insert(root, "end", text=vol, image=self.unchecked_image)
                self.checkbox_vars[item] = tk.BooleanVar(value=False)

    def build_vm_tree(self):
        root = self.vm_tree.insert("", "end", text="Virtual Machines", open=True)
        if hasattr(self.master, 'virtual_machines') and self.master.virtual_machines:
            for vm in self.master.virtual_machines:
                item = self.vm_tree.insert(root, "end", text=vm, image=self.unchecked_image)
                self.checkbox_vars[item] = tk.BooleanVar(value=False)

    def build_app_tree(self):
        root = self.app_tree.insert("", "end", text="Applications", open=True)
        if hasattr(self.master, 'applications') and self.master.applications:
            for app in self.master.applications:
                item = self.app_tree.insert(root, "end", text=app, image=self.unchecked_image)
                self.checkbox_vars[item] = tk.BooleanVar(value=False)

    def on_tree_click(self, event):
        tree = event.widget
        item = tree.identify_row(event.y)
        if item:
            self.toggle_checkbox(item, tree)

    def toggle_checkbox(self, item, tree):
        if item in self.checkbox_vars:
            current_state = self.checkbox_vars[item].get()
            self.checkbox_vars[item].set(not current_state)

            if self.checkbox_vars[item].get():
                tree.item(item, image=self.checked_image)
                item_text = tree.item(item, "text")

                if tree == self.vol_tree:
                    if "Volumes" not in self.checked_items:
                        self.checked_items["Volumes"] = {}
                    self.checked_items["Volumes"][item_text] = self.master.volumes_with_size[item_text]['UsedSpaceGB']
                elif tree == self.vm_tree:
                    if "Virtual Machines" not in self.checked_items:
                        self.checked_items["Virtual Machines"] = {}
                    self.checked_items["Virtual Machines"][item_text] = 0
                elif tree == self.app_tree:
                    if "Applications" not in self.checked_items:
                        self.checked_items["Applications"] = {}
                    self.checked_items["Applications"][item_text] = 0
            else:
                tree.item(item, image=self.unchecked_image)
                item_text = tree.item(item, "text")

                if tree == self.vol_tree:
                    if "Volumes" in self.checked_items and item_text in self.checked_items["Volumes"]:
                        del self.checked_items["Volumes"][item_text]
                        if not self.checked_items["Volumes"]:
                            del self.checked_items["Volumes"]
                elif tree == self.vm_tree:
                    if "Virtual Machines" in self.checked_items and item_text in self.checked_items["Virtual Machines"]:
                        del self.checked_items["Virtual Machines"][item_text]
                        if not self.checked_items["Virtual Machines"]:
                            del self.checked_items["Virtual Machines"]
                elif tree == self.app_tree:
                    if "Applications" in self.checked_items and item_text in self.checked_items["Applications"]:
                        del self.checked_items["Applications"][item_text]
                        if not self.checked_items["Applications"]:
                            del self.checked_items["Applications"]

            self.vol_tree.update_idletasks()
            self.vm_tree.update_idletasks()
            self.app_tree.update_idletasks()

    def on_single_click(self, event):
        pass



BACKING UP 
import subprocess
import os

def backup_windows_directory(backup_item, backup_destination, backup_user, destination_user):
    """
    Backs up a Windows directory using SFTP over SSH.

    Args:
        backup_item (str): The source directory (e.g., "C:\").
        backup_destination (str): The destination directory (e.g., "D:\").
        backup_user (str): Username on the source machine.
        destination_user (str): Username on the destination machine.

    Returns:
        None. Prints the result of the backup operation.
    """

    backup_item_ip = "2.2.2.2"
    backup_destination_ip = "3.3.3.3"

    sftp_command = f'sftp -C -b - {backup_user}@{backup_item_ip}'

    remote_ssh_command = f'ssh {destination_user}@{backup_destination_ip} "{sftp_command}"'

    sftp_script = f"""
    lcd "{backup_item}"
    cd "{backup_destination}"
    mirror -R .
    bye
    """

    try:
        process = subprocess.Popen(
            remote_ssh_command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate(input=sftp_script)

        if process.returncode == 0:
            print("Backup successful:")
            print(stdout)
        else:
            print("Backup failed:")
            print(stderr)

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
backup_item = "C:\\"
backup_destination = "D:\\"
backup_user = "BAK1"
destination_user = "STOR1"

backup_windows_directory(backup_item, backup_destination, backup_user, destination_user)

RESTORING
import subprocess

def restore_windows_directory(backup_item, backup_destination, backup_user, destination_user):
    """
    Restores a Windows directory from a backup using SFTP over SSH.

    Args:
        backup_item (str): The destination directory (e.g., "C:\").
        backup_destination (str): The source directory (e.g., "D:\").
        backup_user (str): Username on the destination machine.
        destination_user (str): Username on the source machine.
    Returns:
        None. Prints the result of the restore operation.
    """

    backup_item_ip = "2.2.2.2"
    backup_destination_ip = "3.3.3.3"

    sftp_command = f'sftp -C -b - {backup_user}@{backup_item_ip}'

    remote_ssh_command = f'ssh {destination_user}@{backup_destination_ip} "{sftp_command}"'

    sftp_script = f"""
    lcd "{backup_destination}"
    cd "{backup_item}"
    mirror -R .
    bye
    """

    try:
        process = subprocess.Popen(
            remote_ssh_command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate(input=sftp_script)

        if process.returncode == 0:
            print("Restore successful:")
            print(stdout)
        else:
            print("Restore failed:")
            print(stderr)

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
backup_item = "C:\\"
backup_destination = "D:\\"
backup_user = "BAK1"
destination_user = "STOR1"

restore_windows_directory(backup_item, backup_destination, backup_user, destination_user)



sftp <username>@<remote_sftp_host>:<port> -b nul






 @staticmethod
    def PairESN(storage_node_pub_key, storage_node_ip, storage_node_username, endpoint_ip, endpoint_username):
        pkey = paramiko.RSAKey.from_private_key_file(app.config.get('Z_KEY_PATH'))
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
        client.connect(hostname=endpoint_ip, username=endpoint_username, port=22, pkey=pkey)
        command = f'Add-Content -Path "$env:USERPROFILE\\.ssh\\authorized_keys" -Value \\"`n{storage_node_pub_key}\\"'
        _, stdout, stderr = client.exec_command(f'powershell.exe -ExecutionPolicy Bypass -Command "{command}"', timeout=999)
        error = stderr.read().decode('utf-8').strip()
        client.close()
        if not error:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.RejectPolicy())
            client.connect(hostname=storage_node_ip, username=storage_node_username, port=22, pkey=pkey)
            command = f'sftp -o StrictHostKeyChecking=no {endpoint_username}@{endpoint_ip}'
            _, stdout, stderr = client.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()
            print("EXIT CODE IS",exit_code)
            client.close()
            if exit_code == 0:
                print("CONNECTED STORAGE TO ENDPOINT")
            else:
                print("AN ERROR OCCURRED: ", stderr)
        else:
            print("PAIR ERROR IS", error)
            return jsonify({"response": "nothing found or an error occurred"}),401





from .  import app, cache, db
from flask import request, jsonify, send_file
from werkzeug.security import check_password_hash
from .Sqlmodels.User import User
from .Sqlmodels.Endpoint import Endpoint
from .Sqlmodels.StorageNode import StorageNode
from .Sqlmodels.ZeroCryptor import ZeroCryptor
from .Sqlmodels.ESNPair import ESNPair
import os, sys,jwt, logging, paramiko
from datetime import datetime, timezone
import time


class Zeroapi:
#MAIN ROUTE METHODS

#Create User Administratively
    @app.route('/zeroapi/v1/adduser', methods=['GET'])
    def adduser():
        newuser  = User(first_name="Rushawn",last_name="Campbell",email="rushawn.campbell@mymona.uwi.edu", username="admin", password="admin123")
        db.session.add(newuser)
        db.session.commit()
        print("status ok user added")
        return jsonify({"stat": "ok user added"})
    #LLog in User
    @app.route('/zeroapi/v1/login', methods=['POST'])
    def login():
        user = None
        if request.method == "POST":
            data = request.get_json()
            uname = data.get('username')
            password = data.get('password')
            user = User.query.filter_by(username=uname).first()
            if user is not None and check_password_hash(user.password, password):
                tokencreationtime = datetime.now(timezone.utc).strftime("%H:%M:%S")
                token  = jwt.encode({'sub':uname,'initime': tokencreationtime}, app.config.get('SECRET_KEY'),algorithm='HS256')  
                return jsonify({
                    "zauth_token": token
                }),200
            else:
                return jsonify({
                    "message": "Login failed, check your username and password then try again.",
                }),401


    #Logout User
    @app.route('/zeroapi/v1/logout', methods=['GET'])
    def logout():
        if request.method == 'GET':
            return jsonify({
            "message": "Log out successful"
        }),200
            
    #Downloads Storage/Endpoint Installers
    @app.route('/zeroapi/v1/download/<download_type>', methods=['GET'])
    def download(download_type):
        user_token= request.headers['Authorization'].split(' ')[1]
        if not user_token:
            return jsonify({"message": "Access token is missing or invalid"}),401
        try:
            decoded = jwt.decode(user_token, app.config['SECRET_KEY'], algorithms=['HS256'])
            namepart= decoded['sub'].lower()
            fetched_user = User.query.filter_by(username=namepart).first()
            if namepart == fetched_user.username.lower():
                try:
                    filename = f'{download_type}.zip'
                    file_path = os.path.join(app.root_path,"..\\","dist", filename) 
        
                    return send_file(
                        file_path,
                        as_attachment=True,
                        download_name=filename  
                    )
                except FileNotFoundError:
                   return jsonify({
                            "message": "The requested resource could not be found. Contact the ZeroDown Support for help.",
                        }),404
                except Exception as e:
                    return jsonify({
                            "message": "Something went wrong. Contact the ZeroDown Support for help.",
                        }),500

        except Exception as e:
            return jsonify({"message": "Access token is missing or invalid"}),401
        
    @app.route('/zeroapi/v1/test_connection', methods=['POST'])
    def test_connection():
        user_token= request.headers['Authorization'].split(' ')[1]
        if not user_token:
            return jsonify({"message": "Access token is missing or invalid"}),401
        try:
            decoded = jwt.decode(user_token, app.config['SECRET_KEY'], algorithms=['HS256'])
            namepart= decoded['sub'].lower()
            fetched_user = User.query.filter_by(username=namepart).first()
            if namepart == fetched_user.username.lower():
                try:
                    data = request.get_json()
                    hostname= data.get('hostname')
                    username=data.get('authorized_user')
                    reg_type=data.get('reg_type')
                    pkey = paramiko.RSAKey.from_private_key_file(app.config.get('Z_KEY_PATH'))
                    
                    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
                    client = paramiko.SSHClient()
                    client.load_system_host_keys()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
                    client.connect(hostname=hostname, username=username,  pkey=pkey)
                    if reg_type == "storagenode":
                        command = "type %USERPROFILE%\\.ssh\\id_rsa.pub"
                        stdin, stdout, stderr = client.exec_command("cmd.exe /c \"" + command + "\"")
                        fetched_pub = stdout.read().decode().strip()
                        error = stderr.read().decode().strip()
                        if not error:
                            return jsonify({"response": fetched_pub}),200
                        return jsonify({"response": fetched_pub}),401
                    client.close()
                    del pkey
                    return jsonify({"response": "Connection Successful"}),200
                except Exception as e:
                    print(e)
                    return jsonify({
                            "response": "Something went wrong. Contact the ZeroDown Support for help.",
                        }),500
            else:
                return jsonify({"response": "Access token is missing or invalid"}),401

        except Exception as e:
            return jsonify({"response": "Access token is missing or invalid"}),401
        


    @app.route('/zeroapi/v1/register/<register_type>', methods=['POST'])
    def register_endpoint(register_type):
        user_token= request.headers['Authorization'].split(' ')[1]
        if not user_token:
            return jsonify({"message": "Access token is missing or invalid"}),401
        try:
            decoded = jwt.decode(user_token, app.config['SECRET_KEY'], algorithms=['HS256'])
            namepart= decoded['sub'].lower()
            fetched_user = User.query.filter_by(username=namepart).first()
            if namepart == fetched_user.username.lower():
                data = request.get_json()
                object_name = data.get('name')
                object_ip= data.get('ip')
                object_user=data.get('authorized_user')
                if register_type == "endpoint":
                    endpoint_object = Endpoint(ip=object_ip, name=object_name, username=object_user)
                    db.session.add(endpoint_object)
                    db.session.commit()
                    return jsonify({"message": "Endpoint Node Registered"}),200
                if register_type == "storagenode":
                    pub_key=data.get('pub_key')
                    storage_object = StorageNode(ip=object_ip, name=object_name, username=object_user,pub_key=pub_key)
                    db.session.add(storage_object)
                    db.session.commit()
                    return jsonify({"message": "Storage Node Registered"}),200
            else:
                return jsonify({"message": "Access token is missing or invalid"}),401
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            line_number = exc_traceback.tb_lineno
            print(f"An exception occurred: {e}")
            print(f"Line number: {line_number}")
            return jsonify({"message": "Access token is missing or invalid"}),401
        
    @app.route('/zeroapi/v1/objects/<object_type>', methods=['GET'])
    def objects(object_type):
        user_token= request.headers['Authorization'].split(' ')[1]
        if not user_token:
            return jsonify({"message": "Access token is missing or invalid"}),401
        try:
            decoded = jwt.decode(user_token, app.config['SECRET_KEY'], algorithms=['HS256'])
            namepart= decoded['sub'].lower()
            fetched_user = User.query.filter_by(username=namepart).first()
            if namepart == fetched_user.username.lower():
                try:
                    if object_type == "endpoints":
                        fetched_endpoints = Endpoint.query.all()
                        endpoint_names = []
                        for endpoint in fetched_endpoints:
                            endpoint_names.append(endpoint.name)

                        return jsonify({
                            "names" : endpoint_names
                        })
                    if object_type == "storagenodes":
                        fetched_storage_nodes = StorageNode.query.all()
                        storage_node_names = []
                        for storage_node in fetched_storage_nodes:
                            #storage_node.append((storage_node.id,storage_node.name))
                            storage_node_names.append(storage_node.name)

                        return jsonify({
                            "names" : storage_node_names
                        })
                    return jsonify({"message": "Hello"})
                except Exception as e:
                    return jsonify({
                            "message": "Something went wrong. Contact the ZeroDown Support for help.",
                        }),500
        except Exception as e:
            return jsonify({"message": "Access token is missing or invalid"}),401
        

    @app.route('/zeroapi/v1/endpoint/listing/<endpoint_name>', methods=['GET'])
    def listing(endpoint_name):
        user_token= request.headers['Authorization'].split(' ')[1]
        if not user_token:
            return jsonify({"message": "Access token is missing or invalid"}),401
        try:
            decoded = jwt.decode(user_token, app.config['SECRET_KEY'], algorithms=['HS256'])
            namepart= decoded['sub'].lower()
            fetched_user = User.query.filter_by(username=namepart).first()
            if namepart == fetched_user.username.lower():

                fetched_endpoint= Endpoint.query.filter_by(name=endpoint_name).first()
                cache.set(f'{namepart}_current_endpoint', fetched_endpoint)
                logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
                try:
                    zcryptobj= ZeroCryptor()
                    encrypted_hostname= fetched_endpoint.ip
                    hostname = zcryptobj._decrypt_data(encrypted_data=encrypted_hostname, type="ENDPOINT")
                    username= fetched_endpoint.username
                    pkey = paramiko.RSAKey.from_private_key_file(app.config.get('Z_KEY_PATH'))
                    client = paramiko.SSHClient()
                    client.load_system_host_keys()
                    client.set_missing_host_key_policy(paramiko.RejectPolicy())
                    client.connect(hostname=hostname, username=username, port=22, pkey=pkey)
                    #command= 'Get-WmiObject Win32_Volume | ForEach-Object {$DriveLetter=$_.DriveLetter; if ($DriveLetter) {Get-ChildItem -Path "$DriveLetter\" -Directory -Recurse -Force | Select-Object -ExpandProperty FullName | ForEach-Object {$_}}} | Out-String -Stream | ForEach-Object {$_.TrimEnd()}'
                    #command = 'Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DriveType > 0" | ForEach-Object {$Volume=$_.DeviceID;$DriveType=$_.DriveType;$DriveTypeString=switch ($DriveType) {0 {"Unknown"} 1 {"No Root Directory"} 2 {"Removable"} 3 {"Local Disk"} 4 {"Network"} 5 {"CD-ROM"} 6 {"RAM Disk"} default {"Other ($DriveType)"}};$TotalSizeGB=[Math]::Round($_.Size / 1GB, 2);$FreeSpaceGB=[Math]::Round($_.FreeSpace / 1GB, 2);$UsedSpaceGB=[Math]::Round(($_.Size - $_.FreeSpace) / 1GB, 2);"$Volume $UsedSpaceGB"} | Out-String -Stream | ForEach-Object {$_.TrimEnd()}'
                    #command='Get-WmiObject Win32_Volume | Select-Object DriveLetter, Capacity, FreeSpace | ConvertTo-Json'
                    #command= r"Get-CimInstance -ClassName Win32_Volume | Select-Object DriveLetter, @{Name='UsedSpace';Expression={$_.Capacity - $_.FreeSpace}} | ConvertTo-Json"
                    #command= r"Get-CimInstance -ClassName Win32_Volume | Select-Object DriveLetter, @{Name='UsedSpaceGB';Expression={[math]::Round(($_.Capacity - $_.FreeSpace) / 1GB, 2)}} | ConvertTo-Json"
                    #command= r"Get-CimInstance -ClassName Win32_Volume | Select-Object DriveLetter, @{Name='DeviceID';Expression={$_.DeviceID}}, @{Name='UsedSpaceGB';Expression={[math]::Round(($_.Capacity - $_.FreeSpace) / 1GB, 2)}} | ConvertTo-Json"
                    #command =r"Get-CimInstance -ClassName Win32_Volume | Select-Object @{Name='DriveLetter';Expression={$_.DriveLetter}}, @{Name='DeviceID';Expression={$_.DeviceID}}, @{Name='SizeGB';Expression={[math]::Round($_.Capacity / 1GB, 2)}} | ConvertTo-Json"
                    command= r"""$Volumes = Get-CimInstance -ClassName Win32_Volume | Select-Object DriveLetter, DeviceID, @{Name='UsedSpaceGB';Expression={[math]::Round(($_.Capacity - $_.FreeSpace) / 1GB, 2)}}; $Output = @{}; foreach ($Volume in $Volumes) { if ($Volume.DriveLetter) { $Output[$Volume.DriveLetter] = @{"DeviceID" = $Volume.DeviceID; "UsedSpaceGB" = $Volume.UsedSpaceGB} } }; $Output | ConvertTo-Json -Depth 5"""
                    _, stdout, stderr = client.exec_command(f'powershell.exe -ExecutionPolicy Bypass -Command "{command}"', timeout=999)
                    vol_dict= stdout.read().decode('utf-8').strip()
                    error = stderr.read().decode('utf-8').strip()
                    client.close()
                    if not error:
                        return jsonify(vol_dict),200
                    else:
                        return jsonify({"response": "nothing found or an error occurred"}),401
                except Exception as e:
                    print(e)
                    return jsonify({
                        "response": "Something went wrong. Contact the ZeroDown Support for help.",
                    }),500
        except Exception as e:
            print(e)
            return jsonify({
                    "response": "Something went wrong. Contact the ZeroDown Support for help.",
            }),500
        

    @app.route('/zeroapi/v1/storage/volumes/<storage_name>', methods=['GET'])
    def volumes(storage_name):
        user_token= request.headers['Authorization'].split(' ')[1]
        if not user_token:
            return jsonify({"message": "Access token is missing or invalid"}),401
        try:
            decoded = jwt.decode(user_token, app.config['SECRET_KEY'], algorithms=['HS256'])
            namepart= decoded['sub'].lower()
            fetched_user = User.query.filter_by(username=namepart).first()
            if namepart == fetched_user.username.lower():

                fetched_storage= StorageNode.query.filter_by(name=storage_name).first()
                cache.set(f'{namepart}_current_storage_node', fetched_storage)
                logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
                try:
                    zcryptobj= ZeroCryptor()
                    encrypted_hostname= fetched_storage.ip
                    hostname = zcryptobj._decrypt_data(encrypted_data=encrypted_hostname, type="STORAGE")
                    username= fetched_storage.username
                    pkey = paramiko.RSAKey.from_private_key_file(app.config.get('Z_KEY_PATH'))
                    client = paramiko.SSHClient()
                    client.load_system_host_keys()
                    client.set_missing_host_key_policy(paramiko.RejectPolicy())
                    client.connect(hostname=hostname, username=username, port=22, pkey=pkey)
                    command = r"""$Volumes = Get-CimInstance -ClassName Win32_Volume | Select-Object DriveLetter, DeviceID, @{Name='AvailableSpaceGB';Expression={[math]::Round(($_.FreeSpace) / 1GB, 2)}}; $Output = @{}; foreach ($Volume in $Volumes) { if ($Volume.DriveLetter) { $Output[$Volume.DriveLetter] = @{"DeviceID" = $Volume.DeviceID; "AvailableSpaceGB" = $Volume.AvailableSpaceGB} } }; $Output | ConvertTo-Json -Depth 5"""
                    _, stdout, stderr = client.exec_command(f'powershell.exe -ExecutionPolicy Bypass -Command "{command}"', timeout=999)
                    vol_dict= stdout.read().decode('utf-8').strip()
                    error = stderr.read().decode('utf-8').strip()
                    client.close()
                    if not error:
                        return jsonify(vol_dict),200
                    else:
                        return jsonify({"response": "nothing found or an error occurred"}),401
                except Exception as e:
                    print(e)
                    return jsonify({
                        "response": "Something went wrong. Contact the ZeroDown Support for help.",
                    }),500
        except Exception as e:
            print(e)
            return jsonify({
                    "response": "Something went wrong. Contact the ZeroDown Support for help.",
            }),500


    @app.route('/zeroapi/v1/endpoint/backupdemand/<endpoint_name>', methods=['POST'])
    def backupdemand(endpoint_name):
        user_token= request.headers['Authorization'].split(' ')[1]
        if not user_token:
            return jsonify({"message": "Access token is missing or invalid"}),401
        try:
            decoded = jwt.decode(user_token, app.config['SECRET_KEY'], algorithms=['HS256'])
            namepart= decoded['sub'].lower()
            fetched_user = User.query.filter_by(username=namepart).first()
            if namepart == fetched_user.username.lower():
                data = request.get_json()
                fetched_endpoint= Endpoint.query.filter_by(name=endpoint_name).first()
                zcryptobj= ZeroCryptor()
                encrypted_hostname= fetched_endpoint.ip
                hostname = zcryptobj._decrypt_data(encrypted_data=encrypted_hostname, type="ENDPOINT")
                username= fetched_endpoint.username
                pkey = paramiko.RSAKey.from_private_key_file(app.config.get('Z_KEY_PATH'))
                client = paramiko.SSHClient()
                client.load_system_host_keys()
                client.set_missing_host_key_policy(paramiko.RejectPolicy())
                client.connect(hostname=hostname, username=username, port=22, pkey=pkey)
                for drive in data:
                    for path,size in data[drive]:
                        command= f'(Get-ChildItem -Path {path} -Force | Measure-Object -Property Length -Sum).Sum'
                        _, stdout, stderr = client.exec_command(f'powershell.exe -ExecutionPolicy Bypass -Command "{command}"', timeout=999)
                        object_size = stdout.read().decode('utf-8').strip()
                        error = stderr.read().decode('utf-8').strip()
                        data[drive][path] = object_size
                    pass
                return jsonify({
                    "response": "DATA IS ",
                }),200

        except Exception as e:
            print(e)
            return jsonify({
                    "response": "Something went wrong. Contact the ZeroDown Support for help.",
            }),500



    @app.route('/zeroapi/v1/backup/on_demand', methods=['POST'])
    def on_demand():
        user_token= request.headers['Authorization'].split(' ')[1]
        if not user_token:
            return jsonify({"message": "Access token is missing or invalid"}),401
        try:
            decoded = jwt.decode(user_token, app.config['SECRET_KEY'], algorithms=['HS256'])
            namepart= decoded['sub'].lower()
            fetched_user = User.query.filter_by(username=namepart).first()
            if namepart == fetched_user.username.lower():

                fetched_endpoint= cache.get(f'{namepart}_current_endpoint')
                fetched_storage = cache.get(f'{namepart}_current_storage_node')

                logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
                try:
                    zcryptobj= ZeroCryptor()
                    storage_node_pub_key = fetched_storage.pub_key
                    storage_node_pub_key = zcryptobj._decrypt_data(encrypted_data=storage_node_pub_key, type="STORAGE")
                    storage_node_ip = fetched_storage.ip
                    storage_node_ip = zcryptobj._decrypt_data(encrypted_data=storage_node_ip, type="STORAGE")
                    storage_node_username = fetched_storage.username
                    endpoint_ip= fetched_endpoint.ip
                    endpoint_ip= zcryptobj._decrypt_data(encrypted_data=endpoint_ip, type="ENDPOINT")
                    endpoint_username = fetched_endpoint.username
                    client, pairing_sftp_exit_code= Zeroapi.PairESN(storage_node_pub_key, storage_node_ip, storage_node_username, endpoint_ip, endpoint_username)
                    if pairing_sftp_exit_code == 0:
                        espnobj = ESNPair(storage_node_id = fetched_storage.id , endpoint_id= fetched_endpoint.id )
                        db.session.add(espnobj)
                        db.session.commit()
                        print("SSH CLIENT IS", client)

                        sftp_commands = [
                                "ls",
                        ]
                        output, error_output, backup_exit_code = Zeroapi.run_backup(client, endpoint_username, endpoint_ip, sftp_commands)
                        if backup_exit_code == 0:
                            print("SFTP Output:", output)
                            if error_output:
                                print("SFTP Standard Error:", error_output)
                            client.close()
                            return jsonify({"response":  pairing_sftp_exit_code}),200
                        else:
                            print("Remote SFTP failed. Exit code:", backup_exit_code)
                            if error_output:
                                print("SFTP Standard Error:", error_output)
                            client.close()
                            return jsonify({"response":  backup_exit_code}),500
                    else:
                        return jsonify({"response":  pairing_sftp_exit_code}),500
                except Exception as e:
                    print(e)
                    return jsonify({"response": -1}),500
        except Exception as e:
            print(e)
            return jsonify({"response":  -1}),500

    #UTILITY FUNCTIONS

    @staticmethod
    def run_backup(client, target_username, target_ip, commands):
        """Runs SFTP commands on the target machine through the intermediary."""
        try:
            command = f'sftp -oBatchMode=yes {target_username}@{target_ip}'
            stdin, stdout, stderr = client.exec_command(command)

            output = ""
            error_output = ""
            for cmd in commands:
                stdin.write(cmd + "\n")
                stdin.flush()
                time.sleep(0.1)  

            stdin.write("bye\n")  
            stdin.flush()
            stdin.close()  

            while not stdout.channel.exit_status_ready():
                if stdout.channel.recv_ready():
                    output += stdout.read().decode()
                if stderr.channel.recv_ready():
                    error_output += stderr.read().decode()
                time.sleep(0.1)

            exit_code = stdout.channel.recv_exit_status()

            return output, error_output, exit_code

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            line_number = exc_traceback.tb_lineno
            print(f"Error running remote SFTP: {e}", "LINE NUMBER IS", line_number)
            return None, None, -1
    
    @staticmethod
    def PairESN(storage_node_pub_key, storage_node_ip, storage_node_username, endpoint_ip, endpoint_username):
        pkey = paramiko.RSAKey.from_private_key_file(app.config.get('Z_KEY_PATH'))
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
        client.connect(hostname=endpoint_ip, username=endpoint_username, port=22, pkey=pkey)
        command = f'Add-Content -Path "$env:USERPROFILE\\.ssh\\authorized_keys" -Value \\"`n{storage_node_pub_key}\\"'
        _, stdout, stderr = client.exec_command(f'powershell.exe -ExecutionPolicy Bypass -Command "{command}"', timeout=999)
        error = stderr.read().decode('utf-8').strip()
        client.close()
        if not error:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.RejectPolicy())
            client.connect(hostname=storage_node_ip, username=storage_node_username, port=22, pkey=pkey)
            command =  f'sftp -oBatchMode=yes {endpoint_username}@{endpoint_ip}'
            stdin, stdout, stderr = client.exec_command(command)
            stdin.write("bye\n")
            stdin.flush()
            stdin.close()
            error = stderr.read().decode().strip()
            output = stdout.read().decode().strip()
            sftp_exit_code = stdout.channel.recv_exit_status()

            return client,sftp_exit_code
        
        else:
            return client, -1










































  @app.route('/zeroapi/v1/backup/on_demand', methods=['POST'])
    def on_demand():
        user_token= request.headers['Authorization'].split(' ')[1]
        if not user_token:
            return jsonify({"message": "Access token is missing or invalid"}),401
        try:
            decoded = jwt.decode(user_token, app.config['SECRET_KEY'], algorithms=['HS256'])
            namepart= decoded['sub'].lower()
            fetched_user = User.query.filter_by(username=namepart).first()
            if namepart == fetched_user.username.lower():

                fetched_endpoint= cache.get(f'{namepart}_current_endpoint')
                fetched_storage = cache.get(f'{namepart}_current_storage_node')

                logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
                try:
                    zcryptobj= ZeroCryptor()
                    storage_node_pub_key = fetched_storage.pub_key
                    storage_node_pub_key = zcryptobj._decrypt_data(encrypted_data=storage_node_pub_key, type="STORAGE")
                    storage_node_ip = fetched_storage.ip
                    storage_node_ip = zcryptobj._decrypt_data(encrypted_data=storage_node_ip, type="STORAGE")
                    storage_node_username = fetched_storage.username
                    endpoint_ip= fetched_endpoint.ip
                    endpoint_ip= zcryptobj._decrypt_data(encrypted_data=endpoint_ip, type="ENDPOINT")
                    endpoint_username = fetched_endpoint.username
                    storage_client, pairing_sftp_exit_code= Zeroapi.PairESN(storage_node_pub_key, storage_node_ip, storage_node_username, endpoint_ip, endpoint_username)
                    print("EXIT CODE IS", pairing_sftp_exit_code)
                    print("SSH CLIENT IS", storage_client)
                    if pairing_sftp_exit_code == 0:
                        espnobj = ESNPair(storage_node_id = fetched_storage.id , endpoint_id= fetched_endpoint.id )
                        db.session.add(espnobj)
                        db.session.commit()

                        #remote_backup_command= r'rsync.exe -avz -e "ssh" --progress Administrator@18.117.188.132:/c/ /d/d_drive_backup/'
                        #remote_backup_command = f'ssh {endpoint_username}@{endpoint_ip} "C:\\msys64\usr\\bin\\rsync.exe -avz --progress C:/ /d/d_drive_backup/"'
                        #remote_backup_command = f'ssh {endpoint_username}@{endpoint_ip} "C:\\msys64\\usr\\bin\\rsync.exe -avz --progress C:/ D:/d_drive_backup/"'
                        #remote_backup_command= f'C:\\msys64\\usr\\bin\\rsync.exe -avz --progress {endpoint_username}@{endpoint_ip}:C:/ D:/d_drive_backup/'
                        #remote_backup_command = f'ssh Administrator@18.117.188.132 "rsync.exe -avz --progress /c/ /d/d_drive_backup/"'
                        #remote_backup_command = f"rsync.exe -avP --progress Administrator@18.117.188.132:/c/Users/Administrators /d/d_drive_backup/"
                        remote_backup_command = f'sftp -oBatchMode=yes {endpoint_username}@{endpoint_ip}'
                        stdin, stdout, stderr = storage_client.exec_command(remote_backup_command)
                        backup_exit_code = stdout.channel.recv_exit_status()
                        output = stdout.read().decode()
                        error_output = stderr.read().decode()
                        if backup_exit_code == 0:
                            print("SFTP Output:", output)
                            if error_output:
                                print("SFTP Standard Error:", error_output)
                            storage_client.close()
                            return jsonify({"response":  pairing_sftp_exit_code}),200
                        else:
                            print("Remote RSYNC failed. Exit code:", backup_exit_code)
                            if error_output:
                                print("RSYNC Standard Error:", error_output)
                            storage_client.close()
                            return jsonify({"response":  backup_exit_code}),500
                    else:
                        return jsonify({"response":  pairing_sftp_exit_code}),500
                except Exception as e:
                    print(e)
                    return jsonify({"response": -1}),500
        except Exception as e:
            print(e)
            return jsonify({"response":  -1}),500



            @staticmethod
    def PairESN(storage_node_pub_key, storage_node_ip, storage_node_username, endpoint_ip, endpoint_username):
        pkey = paramiko.RSAKey.from_private_key_file(app.config.get('Z_KEY_PATH'))
        storage_client = paramiko.SSHClient()
        storage_client.load_system_host_keys()
        storage_client.set_missing_host_key_policy(paramiko.RejectPolicy())
        storage_client.connect(hostname=endpoint_ip, username=endpoint_username, port=22, pkey=pkey)
        command = f'Add-Content -Path "$env:USERPROFILE\\.ssh\\authorized_keys" -Value \\"`n{storage_node_pub_key}\\"'
        _, stdout, stderr = storage_client.exec_command(f'powershell.exe -ExecutionPolicy Bypass -Command "{command}"', timeout=999)
        error = stderr.read().decode('utf-8').strip()
        
        if not error:
            endpoint_client = paramiko.SSHClient()
            endpoint_client.load_system_host_keys()
            endpoint_client.set_missing_host_key_policy(paramiko.RejectPolicy())
            endpoint_client.connect(hostname=storage_node_ip, username=storage_node_username, port=22, pkey=pkey)
            command =  f'ssh -o StrictHostKeyChecking=no {endpoint_username}@{endpoint_ip} "exit"'
            stdin, stdout, stderr = endpoint_client.exec_command(command)
            error = stderr.read().decode().strip()
            output = stdout.read().decode().strip()
            if not error:
                sftp_exit_code = stdout.channel.recv_exit_status()
                endpoint_client.close()
                return storage_client,sftp_exit_code
            return _, -1
        else:
            return _, -1



































            import paramiko
import os

def configure_rclone_and_execute(machine_b_ip, machine_b_user,
                                machine_c_ip, machine_c_user,
                                machine_c_remote_path, machine_b_local_path):
    """Configures rclone on Machine B and executes the rclone command."""

    try:
        # Establish SSH connection to Machine B
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(machine_b_ip, username=machine_b_user) # removed password

        sftp = ssh.open_sftp()

        # Create rclone.conf content
        rclone_conf = f"""
        [machine_c_remote]
        type = sftp
        host = {machine_c_ip}
        user = {machine_c_user}
        root = /
        """

        # Transfer rclone.conf to Machine B
        sftp.putfo(io.StringIO(rclone_conf), os.path.expanduser("~/.config/rclone/rclone.conf"))

        # Execute rclone command on Machine B
        command = f"rclone sync machine_c_remote:{machine_c_remote_path} {machine_b_local_path}"
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()

        print("Rclone output:", output)
        print("Rclone error:", error)

        sftp.close()
        ssh.close()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    import io

    machine_b_ip = "MACHINE_B_IP"
    machine_b_user = "MACHINE_B_USER"

    machine_c_ip = "MACHINE_C_IP"
    machine_c_user = "MACHINE_C_USER"

    machine_c_remote_path = "/path/to/remote/folder"
    machine_b_local_path = "C:\\path\\to\\local\\folder"

    configure_rclone_and_execute(machine_b_ip, machine_b_user,
                                machine_c_ip, machine_c_user,
                                machine_c_remote_path, machine_b_local_path)




import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

@app.route('/zeroapi/v1/backup/on_demand', methods=['POST'])
async def on_demand():
    user_token = request.headers.get('Authorization', '').split(' ')[-1]
    if not user_token:
        return jsonify({"message": "Access token is missing or invalid"}), 401

    try:
        decoded = jwt.decode(user_token, app.config['SECRET_KEY'], algorithms=['HS256'])
        namepart = decoded['sub'].lower()
        fetched_user = User.query.filter_by(username=namepart).first()
        if namepart != fetched_user.username.lower():
            return jsonify({"message": "Invalid user"}), 401

        fetched_endpoint = cache.get(f'{namepart}_current_endpoint')
        fetched_storage = cache.get(f'{namepart}_current_storage_node')

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        zcryptobj = ZeroCryptor()
        storage_node_pub_key = zcryptobj._decrypt_data(encrypted_data=fetched_storage.pub_key, type="STORAGE")
        storage_node_ip = zcryptobj._decrypt_data(encrypted_data=fetched_storage.ip, type="STORAGE")
        storage_node_username = fetched_storage.username
        endpoint_ip = zcryptobj._decrypt_data(encrypted_data=fetched_endpoint.ip, type="ENDPOINT")
        endpoint_username = fetched_endpoint.username

        storage_conn_id, pairing_sftp_exit_code = await Zeroapi.pair_esn(storage_node_pub_key, storage_node_ip, storage_node_username, endpoint_ip, endpoint_username)
        if pairing_sftp_exit_code != 0:
            return jsonify({"response": pairing_sftp_exit_code}), 500

        espnobj = ESNPair(storage_node_id=fetched_storage.id, endpoint_id=fetched_endpoint.id)
        db.session.add(espnobj)
        db.session.commit()

        data = request.get_json()
        selected_storage_volumes = data.get('backup_destination')
        remote_folder = f"C:\\Users\\{endpoint_username}\\Desktop"

        if "Volumes" in selected_storage_volumes:
            selected_storage_volumes = selected_storage_volumes['Volumes'].keys()

            async def run_sftp_in_thread(vol):
                backup_destination = f'{vol}\\'
                sftp_commands = [
                    f'get -r {remote_folder} {backup_destination}',
                    'bye'
                ]
                output, error_output, backup_exit_code = await Zeroapi.run_remote_sftp(storage_conn_id, endpoint_username, endpoint_ip, sftp_commands)

                return backup_exit_code, error_output

            async def process_volumes():
                tasks = [run_sftp_in_thread(vol) for vol in selected_storage_volumes]
                results = await asyncio.gather(*tasks)
                return results

            results = await process_volumes()
            Zeroapi.ssh_connection_pool.close_connection(storage_conn_id)

            for backup_exit_code, error_output in results:
                if backup_exit_code != 0:
                    print("Remote SFTP failed. Exit code:", backup_exit_code)
                    if error_output:
                        print("SFTP Standard Error:", error_output)
                    return jsonify({"response": backup_exit_code}), 500

            return jsonify({"response": 0}), 200

        else:
            Zeroapi.ssh_connection_pool.close_connection(storage_conn_id)
            return jsonify({"response": 0}), 200

    except Exception as e:
        print(e)
        return jsonify({"response": -1}), 500















import csv

def write_log_to_csv(log_data, filename="log.csv"):
    """
    Writes log data to a CSV file.  Handles the case where the file
    may or may not already exist.

    Args:
        log_data (dict): A dictionary containing the log data.
            Expected keys: 'time', 'type', 'description', 'level'.
        filename (str, optional): The name of the CSV file.
            Defaults to "log.csv".
    """
    # Define the header row (column names)
    header = ['time', 'type', 'description', 'level']

    # Check if the file exists to determine if we need to write the header
    write_header = True
    try:
        with open(filename, 'r', newline='') as csvfile:
            # Use csv.Sniffer to determine if the file has a header
            has_header = csv.Sniffer().has_header(csvfile.read(1024)) # Read the first 1024 bytes
            if has_header:
                write_header = False # if there is a header, don't write another one
    except FileNotFoundError:
        # If the file doesn't exist, we definitely need to write the header
        write_header = True
    except csv.Error:
        # Handle other csv errors, like empty file, by writing the header
        write_header = True

    # Write the data to the CSV file
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        if write_header:
            writer.writeheader()  # Write the header row
        writer.writerow(log_data)  # Write the data row

if __name__ == "__main__":
    # Example log data
    log_entry = {
        'time': '2025-10-25 22:33',
        'type': 'endpoint registration',
        'description': 'Registered endpoint One successfully',
        'level': 'Info'
    }

    # Write the log data to log.csv
    write_log_to_csv(log_entry)

    print(f"Log entry written to log.csv")
