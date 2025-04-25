from .  import app, cache, db
from flask import request, jsonify, send_file
from werkzeug.security import check_password_hash
from .Sqlmodels.User import User
from .Sqlmodels.Endpoint import Endpoint
from .Sqlmodels.StorageNode import StorageNode
from .Sqlmodels.ZeroCryptor import ZeroCryptor
from .Sqlmodels.ESNPair import ESNPair
from .Sqlmodels.BackupJob import BackupJob
from .Sqlmodels.ScheduledJob import ScheduledJob
import os, sys,jwt, logging, paramiko, uuid
from datetime import datetime, timezone
import time
import threading


class Zeroapi:
    backup_in_progress = 0
    backup_with_errors = {}
    backup_with_success = {}

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


    @app.route('/zeroapi/v1/backup/restore', methods=['POST'])
    def restore():
        user_token= request.headers['Authorization'].split(' ')[1]
        if not user_token:
            return jsonify({"message": "Access token is missing or invalid"}),401
        try:
            decoded = jwt.decode(user_token, app.config['SECRET_KEY'], algorithms=['HS256'])
            namepart= decoded['sub'].lower()
            fetched_user = User.query.filter_by(username=namepart).first()
            if namepart == fetched_user.username.lower():
                pass
        except Exception as e:
            print(e)
            return jsonify({"response":  -1}),500
        

    @app.route('/zeroapi/v1/backup/first_time', methods=['POST'])
    def first_time():
        user_token = request.headers.get('Authorization', '').split(' ')[-1]
        if not user_token:
            return jsonify({"response": -1}),500
        try:
            decoded = jwt.decode(user_token, app.config['SECRET_KEY'], algorithms=['HS256'])
            namepart = decoded['sub'].lower()
            fetched_user = User.query.filter_by(username=namepart).first()
            if namepart != fetched_user.username.lower():
                return jsonify({"response": -1}),500
            
            data = request.get_json()
    
            fetched_endpoint = cache.get(f'{namepart}_current_endpoint')
            fetched_storage = cache.get(f'{namepart}_current_storage_node')
    
            zcryptobj = ZeroCryptor()
            storage_node_pub_key = zcryptobj._decrypt_data(encrypted_data=fetched_storage.pub_key, type="STORAGE")
            storage_node_ip = zcryptobj._decrypt_data(encrypted_data=fetched_storage.ip, type="STORAGE")
            storage_node_username = fetched_storage.username
            storage_node_id = fetched_storage.id
            endpoint_ip = zcryptobj._decrypt_data(encrypted_data=fetched_endpoint.ip, type="ENDPOINT")
            endpoint_username = fetched_endpoint.username
            endpoint_id = fetched_endpoint.id
            storage_client, pairing_sftp_exit_code, isexists_code,  isexists_esn_pair_id = Zeroapi.PairESN(storage_node_id, storage_node_pub_key, storage_node_ip, storage_node_username, endpoint_id, endpoint_ip, endpoint_username)
    
            if pairing_sftp_exit_code != 0:
                return jsonify({"response": pairing_sftp_exit_code}), 500
    
            if isexists_code == 0:
                esnpair_id = str(uuid.uuid4())
                espnobj = ESNPair( storage_node_id= storage_node_id, endpoint_id= endpoint_id, id=esnpair_id)
                db.session.add(espnobj)
                db.session.commit()
            else:
                esnpair_id = isexists_esn_pair_id
    
            selected_storage_volumes = data.get('backup_destinations')
            remote_folder = f"C:\\Users\\{endpoint_username}\\Desktop"
            job_id = str(uuid.uuid4())
    
            def handle_sftp_result(output, error_output, backup_exit_code):
                if backup_exit_code == 0 and not error_output:
                    return backup_exit_code
                else:
                    print(f"Remote SFTP failed. Exit code: {backup_exit_code}, Error: {error_output}")
                    return -1
    
            def run_backup_thread():
                if "Volumes" in selected_storage_volumes:
                    selected_storage_volumes_list = selected_storage_volumes['Volumes'].keys()
                    for vol in selected_storage_volumes_list:
                        backup_destination = f'{vol}\\'
                        sftp_commands = [
                            f'get -r {remote_folder} {backup_destination}',
                            'bye'
                        ]
                        output, error_output, backup_exit_code = Zeroapi.run_backup(storage_client, endpoint_username, endpoint_ip, sftp_commands)
                        result = handle_sftp_result(output, error_output, backup_exit_code)
                        
                        if result == 0:
                            if job_id in Zeroapi.backup_with_success:
                                Zeroapi.backup_with_success[job_id].append(vol)
                            else:
                                Zeroapi.backup_with_success[job_id] = [vol]
                        else:
                            if job_id in Zeroapi.backup_with_errors:
                                Zeroapi.backup_with_errors[job_id].append(vol)
                            else:
                                Zeroapi.backup_with_errors[job_id] = [vol]
                    storage_client.close()
            threading.Thread(target=run_backup_thread).start()
            job_name = data.get('name')
            backupjob = BackupJob( esnpair=esnpair_id, name=job_name, target=str(data.get('backup_targets')), destination=str(data.get('backup_destinations')), id=job_id)
            db.session.add(backupjob)
            db.session.commit()
            return jsonify({"in_progress": len(selected_storage_volumes), "job_id":job_id }), 200
    
        except Exception as e:
            print("ERROR IS", e)
            return jsonify({"in_progress": -1}),500
        
    
    @app.route('/zeroapi/v1/backup/schedule', methods=['POST'])
    def schedule():
        user_token = request.headers.get('Authorization', '').split(' ')[-1]
        if not user_token:
            return jsonify({"response": -1}),500
        try:
            decoded = jwt.decode(user_token, app.config['SECRET_KEY'], algorithms=['HS256'])
            namepart = decoded['sub'].lower()
            fetched_user = User.query.filter_by(username=namepart).first()
            if namepart != fetched_user.username.lower():
                return jsonify({"response": -1}),500
            data = request.get_json()
            
            fetched_endpoint = cache.get(f'{namepart}_current_endpoint')
            fetched_storage = cache.get(f'{namepart}_current_storage_node')

            zcryptobj = ZeroCryptor()
            storage_node_pub_key = zcryptobj._decrypt_data(encrypted_data=fetched_storage.pub_key, type="STORAGE")
            storage_node_ip = zcryptobj._decrypt_data(encrypted_data=fetched_storage.ip, type="STORAGE")
            storage_node_username = fetched_storage.username
            storage_node_id = fetched_storage.id
            endpoint_ip = zcryptobj._decrypt_data(encrypted_data=fetched_endpoint.ip, type="ENDPOINT")
            endpoint_username = fetched_endpoint.username
            endpoint_id = fetched_endpoint.id
            storage_client, pairing_sftp_exit_code, isexists_code,  isexists_esn_pair_id = Zeroapi.PairESN(storage_node_id, storage_node_pub_key, storage_node_ip, storage_node_username, endpoint_id, endpoint_ip, endpoint_username)
            storage_client.close()

            if pairing_sftp_exit_code != 0:
                return jsonify({"response": "Preflight Test Failed, We Couldn't Connect Your Endpoint To The Storage Node. Verify that SSH Server Service is running on both."}), 500
    
            if isexists_code == 0:
                esnpair_id = str(uuid.uuid4())
                espnobj = ESNPair( storage_node_id=storage_node_id, endpoint_id= endpoint_id, id=esnpair_id)
                db.session.add(espnobj)
                db.session.commit()
            else:
                esnpair_id = isexists_esn_pair_id
                
    
            job_id = str(uuid.uuid4())
            job_name = data.get('name')

            backupjob = BackupJob( esnpair=esnpair_id, name=job_name, target=str(data.get('backup_targets')), destination=str(data.get('backup_destinations')), id=job_id)
            db.session.add(backupjob)
            #db.session.commit()
        
            sch_datetime = data.get('sch_datetime')
            sch_frequency = data.get('sch_frequency')
            sch_day = data.get('sch_day')

            print ("DATE TIME TYPE IS", type(sch_datetime))
            print ("DAY TYPE IS", type(sch_day))
            print ("FREQUENCY TYPE IS", type(sch_frequency))

            if sch_frequency == "Weekly":
                scheduled_job = ScheduledJob(job_id=job_id, frequency=sch_frequency, sch_datetime = sch_datetime, sch_day = sch_day )
            else:
                scheduled_job = ScheduledJob(job_id=job_id, frequency=sch_frequency, sch_datetime = sch_datetime)
            
            db.session.add(scheduled_job)
            #db.session.flush()
            db.session.commit()
            print("ADDED JOB AND SCHEDULE")
            return jsonify({"response": "Your Backup Job Was Created And Will Execute As Scheduled"}), 200

        except Exception as e:
            print("ERROR IS", e)
            return jsonify({"in_progress": -1}),500
        
        
    @app.route('/zeroapi/v1/backup/get_status', methods=['POST'])
    def get_status():
        user_token = request.headers.get('Authorization', '').split(' ')[-1]
        if not user_token:
            return jsonify({"response": -1}),500
        try:
            decoded = jwt.decode(user_token, app.config['SECRET_KEY'], algorithms=['HS256'])
            namepart = decoded['sub'].lower()
            fetched_user = User.query.filter_by(username=namepart).first()
            if namepart == fetched_user.username.lower():
                job_id = request.get_json()
                job_id = job_id.get('job_id')
            if job_id in Zeroapi.backup_with_success and job_id in Zeroapi.backup_with_errors:
                return jsonify({"success":  Zeroapi.backup_with_success[job_id], "error" : Zeroapi.backup_with_errors[job_id] }),200
            elif job_id not in Zeroapi.backup_with_success and job_id in Zeroapi.backup_with_errors:
                return jsonify({"success":  [], "error" : Zeroapi.backup_with_errors[job_id] }),200
            elif job_id in Zeroapi.backup_with_success and job_id not in Zeroapi.backup_with_errors:
                return jsonify({"success":  Zeroapi.backup_with_success[job_id], "error" : [] }),200
            else:
                return jsonify({"success": [], "error" : [] }),200
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            line_number = exc_traceback.tb_lineno
            return jsonify({"response": -1}),500

    #UTILITY FUNCTIONS
    @staticmethod
    def run_backup(storage_client, endpoint_username, endpoint_ip, commands):
        try:
            command = f'sftp -oBatchMode=yes {endpoint_username}@{endpoint_ip}'
            stdin, stdout, stderr = storage_client.exec_command(command)

            output = ""
            error_output = ""
            for cmd in commands:
                stdin.write(cmd + "\n")
                stdin.flush()
                time.sleep(0.1)  

            stdin.close()  

            while not stdout.channel.exit_status_ready():
                if stdout.channel.recv_ready():
                    output += stdout.read().decode()
                if stderr.channel.recv_ready():
                    error_output += stderr.read().decode()
                time.sleep(0.1)

            exit_code = stdout.channel.recv_exit_status()
            storage_client.close()
            return output, error_output, exit_code

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            line_number = exc_traceback.tb_lineno
            print(f"Error running remote SFTP: {e}", "LINE NUMBER IS", line_number)
            return None, None, -1
    
    @staticmethod
    def PairESN(storage_node_id,storage_node_pub_key, storage_node_ip, storage_node_username, endpoint_id, endpoint_ip, endpoint_username):
        isexist =  ESNPair.query.filter(ESNPair.storage_node_id == storage_node_id, ESNPair.endpoint_id == endpoint_id).first()
        if isexist != None:
            pkey = paramiko.RSAKey.from_private_key_file(app.config.get('Z_KEY_PATH'))
            storage_client = paramiko.SSHClient()
            storage_client.load_system_host_keys()
            storage_client.set_missing_host_key_policy(paramiko.RejectPolicy())
            storage_client.connect(hostname=storage_node_ip, username=storage_node_username, port=22, pkey=pkey)
            command =  f'sftp -oBatchMode=yes {endpoint_username}@{endpoint_ip}'
            stdin, stdout, stderr = storage_client.exec_command(command)
            stdin.write("bye\n")
            stdin.flush()
            stdin.close()
            error = stderr.read().decode().strip()
            output = stdout.read().decode().strip()
            sftp_exit_code = stdout.channel.recv_exit_status()
            return storage_client, sftp_exit_code, -2, isexist.id
        else:
            pkey = paramiko.RSAKey.from_private_key_file(app.config.get('Z_KEY_PATH'))
            endpoint_client = paramiko.SSHClient()
            endpoint_client.load_system_host_keys()
            endpoint_client.set_missing_host_key_policy(paramiko.RejectPolicy())
            endpoint_client.connect(hostname=endpoint_ip, username=endpoint_username, port=22, pkey=pkey)
            command = f'Add-Content -Path "$env:USERPROFILE\\.ssh\\authorized_keys" -Value \\"`n{storage_node_pub_key}\\"'
            _, stdout, stderr = endpoint_client.exec_command(f'powershell.exe -ExecutionPolicy Bypass -Command "{command}"', timeout=999)
            error = stderr.read().decode('utf-8').strip()
            endpoint_client.close()
            if not error:
                storage_client = paramiko.SSHClient()
                storage_client.load_system_host_keys()
                storage_client.set_missing_host_key_policy(paramiko.RejectPolicy())
                storage_client.connect(hostname=storage_node_ip, username=storage_node_username, port=22, pkey=pkey)
                command =  f'sftp -oBatchMode=yes {endpoint_username}@{endpoint_ip}'
                stdin, stdout, stderr = storage_client.exec_command(command)
                stdin.write("bye\n")
                stdin.flush()
                stdin.close()
                error = stderr.read().decode().strip()
                output = stdout.read().decode().strip()
                sftp_exit_code = stdout.channel.recv_exit_status()
                return storage_client,sftp_exit_code, 0, None
            else:
                return _, -1, -1, None
    
    @staticmethod
    def UnPairESN(storage_node_id,storage_node_pub_key, storage_node_ip, storage_node_username, endpoint_id, endpoint_ip, endpoint_username):
        pass #for later

