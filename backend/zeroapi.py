from .  import app, db
from flask import request, jsonify, send_file
from werkzeug.security import check_password_hash
from .Sqlmodels.User import User
from .Sqlmodels.Endpoint import Endpoint
from .Sqlmodels.StorageNode import StorageNode
from .Sqlmodels.ZeroCryptor import ZeroCryptor
import os, sys,jwt, logging, json, paramiko
from datetime import datetime, timezone

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
                    #"message": "Login Successful",
                    #"first_name": user.first_name,
                    #"last_name": user.last_name,
                    #"user_id": user.user_id,
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
                print("WITHOUT EXCEPTION")
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
                            #endpoint_names.append((endpoint.id,endpoint.name))
                            endpoint_names.append(endpoint.name)

                        return jsonify({
                            "names" : endpoint_names
                        })
                    if object_type == "storagenodes":
                        pass
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
                        print(vol_dict)
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

#HELPER METHODS
    def get_windows_volumes(hostname, username, port=22, key_filename=None):
        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.RejectPolicy())


            logging.info(f"Using key file: {key_filename}")
            key = paramiko.RSAKey.from_private_key_file(key_filename)
            client.connect(hostname=hostname, username=username, port=port, pkey=key)

            command="powershell.exe -command \" Get-WmiObject Win32_Volume | Select-Object DriveLetter, Capacity, FreeSpace | ConvertTo-Json\""
            """Get-WmiObject Win32_LogicalDisk | Select-Object DeviceID, VolumeName, @{Label="Capacity (Bytes)";Expression={$_.Size}}, @{Label="Free Space (Bytes)";Expression={$_.FreeSpace}}"""
            """(Get-ChildItem D:\ISO -force -Recurse -ErrorAction SilentlyContinue| measure Length -sum).sum / 1Gb"""
            
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