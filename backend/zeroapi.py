from .  import app, cache, db, scheduler
from flask import request, jsonify, send_file
from werkzeug.security import check_password_hash
from .Sqlmodels.User import User
from .Sqlmodels.Endpoint import Endpoint
from .Sqlmodels.StorageNode import StorageNode
from .Sqlmodels.ZeroCryptor import ZeroCryptor
from .Sqlmodels.ESNPair import ESNPair
from .Sqlmodels.BackupJob import BackupJob
from .Sqlmodels.ScheduledJob import ScheduledJob
import os, sys,jwt, logging, paramiko, uuid, time, json, ast, threading
from datetime import datetime

class Zeroapi:
    backup_in_progress = 0
    backup_with_errors = {}
    backup_with_success = {}

    #creates user administratively
    @app.route('/zeroapi/v1/adduser', methods=['GET'])
    def adduser():
        newuser  = User(first_name="Rushawn",last_name="Campbell",email="rushawn.campbell@mymona.uwi.edu", username="admin", password="admin123")
        db.session.add(newuser)
        db.session.commit()
        print("status ok user added")
        return jsonify({"stat": "ok user added"})
    
    #Log in User
    @app.route('/zeroapi/v1/login', methods=['POST'])
    def login():
        user = None
        if request.method == "POST":
            data = request.get_json()
            uname = data.get('username')
            password = data.get('password')
            user = User.query.filter_by(username=uname).first()
            if user is not None and check_password_hash(user.password, password):
                tokencreationtime = datetime.now().strftime("%H:%M:%S")
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
            if namepart == fetched_user.username.lower(): #only allows download from token authenticated users
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

    #Tests ssh connections between Zerodown server, endpoints and storage nodes.  
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
                    pkey = paramiko.RSAKey.from_private_key_file(app.config.get('Z_KEY_PATH')) #get Zerodown server's private key 
                    
                    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
                    client = paramiko.SSHClient()
                    client.load_system_host_keys()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #Auto add ip to known host keys for first time connections only
            
                    client.connect(hostname=hostname, username=username,  pkey=pkey)
                    if reg_type == "storagenode":
                        command = "type %USERPROFILE%\\.ssh\\id_rsa.pub" 
                        stdin, stdout, stderr = client.exec_command("cmd.exe /c \"" + command + "\"") #using cmd to get storage node public key
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
        

    #registers storage node and endpoints
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
                    #creates storage node record  ip address is  encrypted in the Endpoint model before upgrading migration to mysql
                    endpoint_object = Endpoint(ip=object_ip, name=object_name, username=object_user)
                    db.session.add(endpoint_object)
                    db.session.commit()
                    return jsonify({"message": "Endpoint Node Registered"}),200
                if register_type == "storagenode": 
                    pub_key=data.get('pub_key')
                    #creates storage node record  ip and public key are encrypted in the StorageNode model before upgrading migration to mysql
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
    
    #Getting storage node, endpoint objects, scheduledjobs,
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
                        endpoints = []
                        for endpoint in fetched_endpoints:
                            endpoints.append({
                                "endpoint_id" : endpoint.id,
                                "endpoint_name": endpoint.name,
                                "endpoint_reg_date": endpoint.created.strftime("%Y-%m-%d %H:%M:%S")
                            })
                        return jsonify({
                            "response" : endpoints
                        })
                    elif object_type == "storagenodes":
                        fetched_storage_nodes = StorageNode.query.all()
                        storagenodes = []
                        for storagenode in fetched_storage_nodes:
                            storagenodes.append({
                                "storage_id" : storagenode.id,
                                "storage_name": storagenode.name,
                                "storage_reg_date": storagenode.created.strftime("%Y-%m-%d %H:%M:%S")
                            })

                        return jsonify({
                            "response" : storagenodes
                        })
                    elif object_type == "endpoint_names":
                        fetched_endpoints = Endpoint.query.all()
                        endpoint_names = []
                        for endpoint in fetched_endpoints:
                            endpoint_names.append(endpoint.name)
                        return jsonify({
                            "response" : endpoint_names
                        })
                    elif object_type == "storage_names":
                        fetched_storage_nodes = StorageNode.query.all()
                        storage_node_names = []
                        for storage_node in fetched_storage_nodes:
                            storage_node_names.append(storage_node.name)

                        return jsonify({
                            "response" : storage_node_names
                        })
                    elif object_type == "scheduled_jobs":
                        fetched_scheduled_jobs = ScheduledJob.query.all()
                        scheduled_jobs = []
                        for scheduled_job in fetched_scheduled_jobs:

                            last_backup = scheduled_job.existing_job.last_backup
                            next_backup = scheduled_job.next_sch_datetime

                            if last_backup:
                                last_backup = scheduled_job.existing_job.last_backup.strftime("%Y-%m-%d %H:%M:%S")
                            else:
                                last_backup = "Not Yet"
                            
                            if next_backup:
                                next_backup = scheduled_job.next_sch_datetime.strftime("%Y-%m-%d %H:%M:%S")
                            else:
                                next_backup = "Not Yet"
                                
                            scheduled_jobs.append({
                                "schedule_id" : scheduled_job.id,
                                "job_name": scheduled_job.existing_job.name,
                                "last_backup": last_backup,
                                "next_backup": next_backup
                            })

                        return jsonify({
                            "response" : scheduled_jobs
                        })
                    return jsonify({"message": "??"})
                except Exception as e:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    line_number = exc_traceback.tb_lineno
                
                    return jsonify({
                            "message": "Something went wrong. Contact the ZeroDown Support for help.",
                        }),500
        except Exception as e:
            return jsonify({"message": "Access token is missing or invalid"}),401
        



    @app.route('/zeroapi/v1/object/<object_type>/<object_id>', methods=['GET'])
    def object(object_type, object_id):
        user_token= request.headers['Authorization'].split(' ')[1]
        if not user_token:
            return jsonify({"message": "Access token is missing or invalid"}),401
        try:
            decoded = jwt.decode(user_token, app.config['SECRET_KEY'], algorithms=['HS256'])
            namepart= decoded['sub'].lower()
            fetched_user = User.query.filter_by(username=namepart).first()
            if namepart == fetched_user.username.lower():
                try:
                    if object_type == "endpoint":
                        fetched_endpoint = Endpoint.query.filter_by(id=object_id).first()
                        fetched_endpoint_dict= {}

                        zcryptobj= ZeroCryptor()
                        encrypted_ip= fetched_endpoint.ip
                        plain_ip = zcryptobj._decrypt_data(encrypted_data=encrypted_ip, type="ENDPOINT")

                        fetched_endpoint_dict['ip'] = plain_ip
                        fetched_endpoint_dict['authorized_user'] = fetched_endpoint.username
                        fetched_endpoint_dict['scheduled_jobs'] =  []
                        fetched_endpoint_dict['storage_nodes'] =  []

                        associated_jobs =  ScheduledJob.query.filter_by(endpoint_id=object_id).all()
                        for job in associated_jobs:
                            fetched_endpoint_dict['scheduled_jobs'].append({
                                "job_id" : job.existing_job.id,
                                "job_name": job.existing_job.name,
                                "target": job.existing_job.target,
                                "destination": job.existing_job.destination
                            })
                        
                        paired_storage_nodes = ESNPair.query.filter_by(endpoint_id=object_id).all()
                        for esnpair in  paired_storage_nodes:
                            fetched_endpoint_dict['storage_nodes'].append({
                                "storage_id" : esnpair.storage_node_id,
                                "storage_name": esnpair.storage_node.name
                            })

                        print("ENDPOINT DICT", fetched_endpoint_dict )
                        return jsonify({
                            "response":fetched_endpoint_dict
                        })
                    
                    elif object_type == "storagenode":
                        fetched_storage_nodes = StorageNode.query.all()
                        storagenodes = []
                        for storagenode in fetched_storage_nodes:
                            storagenodes.append({
                                "storage_id" : storagenode.id,
                                "storage_name": storagenode.name,
                                "storage_reg_date": storagenode.created.strftime("%Y-%m-%d %H:%M:%S")
                            })

                        return jsonify({
                            "response" : storagenodes
                        })
                    
                    return jsonify({"message": "??"})
                except Exception as e:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    line_number = exc_traceback.tb_lineno
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

    #Getting Endpoints available and consumed size
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

    #One time backup endpoint
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
    
            zcryptobj = ZeroCryptor() #custom cryptography object
            storage_node_pub_key = zcryptobj._decrypt_data(encrypted_data=fetched_storage.pub_key, type="STORAGE")
            storage_node_ip = zcryptobj._decrypt_data(encrypted_data=fetched_storage.ip, type="STORAGE") #decrypted storage node ip
            storage_node_username = fetched_storage.username
            storage_node_id = fetched_storage.id
            endpoint_ip = zcryptobj._decrypt_data(encrypted_data=fetched_endpoint.ip, type="ENDPOINT")  #decrypted endpoint  ip
            endpoint_username = fetched_endpoint.username
            endpoint_id = fetched_endpoint.id
            #pairing endpoint and storage
            storage_client, pairing_sftp_exit_code, isexists_code,  isexists_esn_pair_id = Zeroapi.PairESN(storage_node_id, storage_node_pub_key, storage_node_ip, storage_node_username, endpoint_id, endpoint_ip, endpoint_username)
    
            #checking for existing pairing returned by Pairesn 
            if pairing_sftp_exit_code != 0:
                return jsonify({"response": pairing_sftp_exit_code}), 500
            #indicates success
            if isexists_code == 0:
                esnpair_id = str(uuid.uuid4())
                espnobj = ESNPair( storage_node_id= storage_node_id, endpoint_id= endpoint_id, id=esnpair_id)
                db.session.add(espnobj)
                db.session.commit()
            else:
                esnpair_id = isexists_esn_pair_id
    
            selected_storage_volumes = data.get('backup_destinations')
            remote_folder_path= f"C:/Users/{endpoint_username}/Desktop" #modified for demo
            remote_folder_name = remote_folder_path.split("/")[-1]
            remote_folder = [ remote_folder_name, remote_folder_path ]
            job_id = str(uuid.uuid4())
    
            #run backup operation in a new thread
            threading.Thread(target=Zeroapi.run_backup_thread, args=(storage_client, endpoint_username, endpoint_ip, selected_storage_volumes, job_id, None, remote_folder)).start()
            job_name = data.get('name')
            backupjob = BackupJob( esnpair=esnpair_id, name=job_name, target=str(data.get('backup_targets')), destination=str(data.get('backup_destinations')), id=job_id)
            db.session.add(backupjob)
            db.session.commit()
            return jsonify({"in_progress": len(selected_storage_volumes), "job_id":job_id }), 200
    
        except Exception as e:
            print("ERROR IS", e)
            return jsonify({"in_progress": -1}),500
        
    
    #schedules backup job
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

            #pairs storage with endpoint if not already done
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

            #testing sftp connection between storage and endpoint
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

            #create backupjob to aid with endpoint and storage node management later
            backupjob = BackupJob( esnpair=esnpair_id, name=job_name, target=str(data.get('backup_targets')), destination=str(data.get('backup_destinations')), id=job_id)
            db.session.add(backupjob)
            db.session.flush()
            
            sch_id = str(uuid.uuid4())
            sch_datetime = data.get('sch_datetime')
            sch_datetime = datetime.strptime(sch_datetime, '%Y-%m-%d %H:%M:%S')
            sch_frequency = data.get('sch_frequency')
            sch_day = data.get('sch_day')
            num_archive_copies = data.get('num_archive_copies')


            if sch_frequency == "Weekly":
                scheduled_job = ScheduledJob(job_id=job_id, frequency=sch_frequency, sch_datetime = sch_datetime, id=sch_id, endpoint_id= endpoint_id, sch_day = sch_day, num_archive_copies= num_archive_copies)
            else:
                scheduled_job = ScheduledJob(job_id=job_id, frequency=sch_frequency, sch_datetime = sch_datetime, id=sch_id, endpoint_id= endpoint_id, num_archive_copies=num_archive_copies)
            
            db.session.add(scheduled_job)
            db.session.commit()

            selected_storage_volumes = data.get('backup_destinations')
            #setting up apscheduler for onetime scheduled job
            if sch_frequency == "One Time":
                scheduler.add_job(
                    func=Zeroapi.run_scheduled_backup,
                    trigger='date',
                    run_date=sch_datetime,
                    args=[job_id, sch_id, selected_storage_volumes ],  
                    id=f"{job_id}:{sch_id}",  
                    replace_existing=True
                )
            #setting up apscheduler for Daily scheduled Cron job
            elif sch_frequency == "Daily":
                scheduler.add_job(
                    func=Zeroapi.run_scheduled_backup,
                    trigger='cron',
                    hour=sch_datetime.hour,
                    minute=sch_datetime.minute,
                    args=[job_id, sch_id, selected_storage_volumes],
                    id=f"{job_id}:{sch_id}",
                    replace_existing=True
                   )
                
            #setting up apscheduler for weekly scheduled Cron job
            elif sch_frequency == "Weekly":
                scheduler.add_job(
                    func=Zeroapi.run_scheduled_backup,
                    trigger='cron',
                    day_of_week=sch_day, 
                    hour=sch_datetime.hour,
                    minute=sch_datetime.minute,
                    args=[job_id, sch_id, selected_storage_volumes],
                    id=f"{job_id}:{sch_id}",
                    replace_existing=True
                )

            #setting up apscheduler for Monthly scheduled Cron job
            elif sch_frequency == "Monthly":
                scheduler.add_job(
                    func=Zeroapi.run_scheduled_backup,
                    trigger='cron',
                    day=sch_datetime.day,
                    hour=sch_datetime.hour,
                    minute=sch_datetime.minute,
                    args=[job_id,sch_id, selected_storage_volumes],
                    id=f"{job_id}:{sch_id}",
                    replace_existing=True
                )
 
            return jsonify({"response": "Your Backup Job Was Created And Will Execute As Scheduled"}), 200

        except Exception as e:
            print("ERROR IS", e)
            return jsonify({"in_progress": -1}),500
        
    #called at intervals from frontend to measure when backup jobs are complete 
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
    #performs the main backup operations(called from in thread)
    @staticmethod
    def run_backup(storage_client, endpoint_username, endpoint_ip, commands, sch_obj=None, destination_folder_name=None,  destination_folder_root=None):
        try:
            num_archive_copies = 0
            num_copies_on_storage = 0
            if sch_obj:
                num_archive_copies = sch_obj.num_archive_copies
                num_copies_on_storage = sch_obj.num_copies_on_storage
                archive_queue_string = sch_obj.archive_queue
                archive_queue = ast.literal_eval(archive_queue_string)
                if num_copies_on_storage == num_archive_copies:
                    full_copy_name=  archive_queue[0]
                    copy_to_remove_name = archive_queue[1]

                    full_copy_path = fr'{destination_folder_root}/{full_copy_name}' #constructing storage node path
                    copy_to_remove_path = fr'{destination_folder_root}/{copy_to_remove_name}'

                    merge_command = fr"Get-ChildItem -Path '{copy_to_remove_path}' -Recurse | Copy-Item -Destination '{full_copy_path}' -Force"
                    remove_command= fr"Remove-Item -Path '{copy_to_remove_path}' -Force -Recurse"

                    stdin, stdout, stderr = storage_client.exec_command(fr'powershell.exe -ExecutionPolicy Bypass -Command "{merge_command}"')
                    exit_status = stdout.channel.recv_exit_status()
                    if exit_status == 0:
                        print(f"Successfully merged contents from '{copy_to_remove_path}' to '{full_copy_path}'.")
                        stdin, stdout, stderr = storage_client.exec_command(fr'powershell.exe -ExecutionPolicy Bypass -Command "{remove_command}"')
                        exit_status = stdout.channel.recv_exit_status()
                        if exit_status == 0:
                            print(f"Successfully removed '{copy_to_remove_path}'.")
                            archive_queue = archive_queue.pop(1)
                            sch_obj.archive_queue = archive_queue
                            db.session.commit()
                        else:
                            error = stderr.read().decode()
                            print(f"Error removing '{copy_to_remove_path}': {error}")
                    else:
                        error = stderr.read().decode()
                        print(f"Error merging contents: {error}")
                else:
                    archive_queue.append(destination_folder_name)
                    sch_obj.archive_queue = str(archive_queue)
                    db.session.commit()

            command = f'sftp -oBatchMode=yes -C {endpoint_username}@{endpoint_ip}'
            stdin, stdout, stderr = storage_client.exec_command(command)

            output = ""
            error_output = ""
            
            print("COMMANDS IN RUN BACKUP ARE", commands)
            for cmd in commands:
                stdin.write(cmd + "\n")
                stdin.flush()
                time.sleep(0.5)  

            stdin.close()  

            while not stdout.channel.exit_status_ready():
                if stdout.channel.recv_ready():
                    output += stdout.read().decode()
                if stderr.channel.recv_ready():
                    error_output += stderr.read().decode()
                time.sleep(0.5)

            exit_code = stdout.channel.recv_exit_status()
            
            storage_client.close()

            if exit_code == 0:
                if sch_obj:
                    num_copies_on_storage+=1
                    sch_obj.num_copies_on_storage= num_copies_on_storage
                    db.session.commit()

            return output, error_output, exit_code

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            line_number = exc_traceback.tb_lineno
            print(f"Error running remote SFTP: {e}", "LINE NUMBER IS", line_number)
            return None, None, -1
    
    @staticmethod
    #pairs storage nodes with endpoints
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
    #handles sftp responses, called within thread
    def handle_sftp_result(output, error_output, backup_exit_code):
       if backup_exit_code == 0 and not error_output:
           return backup_exit_code
       else:
           print(f"Remote SFTP failed. Exit code: {backup_exit_code}, Error: {error_output}")
           return -1
       
    @staticmethod
    #invoked by thread caller, initiates the backup operation
    def run_backup_thread(storage_client, endpoint_username, endpoint_ip,selected_storage_volumes, job_id, sch_id, backup_paths):
        with app.app_context():
            print("BACKUP PATHS ARE", backup_paths)
            sch_obj= ScheduledJob.query.filter_by(id=sch_id).first()
            archive_queue_string = sch_obj.archive_queue
            archive_queue = ast.literal_eval(archive_queue_string)

            fetched_job = BackupJob.query.filter_by(id=job_id).first()
            fetched_job_name = fetched_job.name.replace(" ","")
            fetched_job_esnpair = fetched_job.esnpair
            isexist = ESNPair.query.filter_by(id = fetched_job_esnpair).first()
            if isexist:
                if "Volumes" in selected_storage_volumes:
                    backup_time = datetime.now()
                    selected_storage_volumes_list = selected_storage_volumes['Volumes'].keys()
                    remote_folder_name = backup_paths[0]
                    destination_folder_path= ""
                    destination_folder_name=""
                    destination_folder_root= ""     
                    
                    for vol in selected_storage_volumes_list:
                        print("Selected Storage Volume is", vol)
                        if len(archive_queue)== 0: #creates full backup folder if archive queue is empty
                            destination_folder_name=f'{fetched_job_name}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'
                            destination_folder_path = fr'{vol}/{destination_folder_name}/{remote_folder_name}'
                            create_full_copy_folder = fr'mkdir "{destination_folder_path}"'
                           
                            stdin, stdout, stderr = storage_client.exec_command(create_full_copy_folder)
                           
                        else: #creates increment folders
                            destination_folder_name = f'{fetched_job_name}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'
                            destination_folder_path = fr'{vol}/{destination_folder_name}/'
                            destination_folder_root =  fr'{vol}/'
                            command =  fr'mkdir "{destination_folder_path}"'
                            stdin, stdout, stderr = storage_client.exec_command(command)
                        sftp_commands =[]
                        
    
                        for path in backup_paths[1:]:
                            if path not in sftp_commands:
                                sftp_commands.append( fr'reget -r "{path}" "{destination_folder_path}"')
                        sftp_commands.append('bye')

                        if sch_obj:
                            if sch_obj.frequency == "One Time":
                                output, error_output, backup_exit_code = Zeroapi.run_backup(storage_client, endpoint_username, endpoint_ip, sftp_commands, sch_obj=None, destination_folder_name=None, destination_folder_root=None)
                            else:   
                                output, error_output, backup_exit_code = Zeroapi.run_backup(storage_client, endpoint_username, endpoint_ip, sftp_commands, sch_obj=sch_obj, destination_folder_name=destination_folder_name, destination_folder_root=destination_folder_root)
                        else:
                            output, error_output, backup_exit_code = Zeroapi.run_backup(storage_client, endpoint_username, endpoint_ip, sftp_commands, sch_obj=None, destination_folder_name=None, destination_folder_root=None)
                        result = Zeroapi.handle_sftp_result(output, error_output, backup_exit_code)
                       
                        if result == 0:
                            if job_id in Zeroapi.backup_with_success:
                                Zeroapi.backup_with_success[job_id].append(vol)
                            else:
                                Zeroapi.backup_with_success[job_id] = [vol]
                            with app.app_context():
                                fetched_backup = BackupJob.query.filter_by(id=job_id).first()
                                if fetched_backup:
                                    fetched_backup.last_backup=backup_time
                                    db.session.commit()
                        else:
                            if job_id in Zeroapi.backup_with_errors:
                                Zeroapi.backup_with_errors[job_id].append(vol)
                            else:
                                Zeroapi.backup_with_errors[job_id] = [vol]
                    storage_client.close() 


    @staticmethod
    #invoked by apscheduler when cron conditions are satisfied as dictated with configured scheduled job frequency
    def run_scheduled_backup(job_id, sch_id, selected_storage_volumes):

        with app.app_context():
            zcryptobj = ZeroCryptor()
            fetched_schedule = ScheduledJob.query.filter_by(id=sch_id).first()
            storage_node_ip = fetched_schedule.existing_job.esn_pair.storage_node.ip
            storage_node_ip = zcryptobj._decrypt_data(encrypted_data=storage_node_ip, type="STORAGE")
            storage_node_username =  fetched_schedule.existing_job.esn_pair.storage_node.username
            endpoint_username =   fetched_schedule.existing_job.esn_pair.endpoint.username
            endpoint_ip =   fetched_schedule.existing_job.esn_pair.endpoint.ip
            endpoint_ip = zcryptobj._decrypt_data(encrypted_data=endpoint_ip, type="ENDPOINT")
            remote_folder = f"C:/Users/{endpoint_username}/Desktop"  #hardcoding volume path for demo 
            remote_folder_name = remote_folder.split('/')[-1]
            pkey = paramiko.RSAKey.from_private_key_file(app.config.get('Z_KEY_PATH'))

            storage_client = paramiko.SSHClient()
            storage_client.load_system_host_keys()
            storage_client.set_missing_host_key_policy(paramiko.RejectPolicy())
            storage_client.connect(hostname=storage_node_ip, username=storage_node_username, port=22, pkey=pkey)

            endpoint_client=paramiko.SSHClient()
            endpoint_client.load_system_host_keys()
            endpoint_client.set_missing_host_key_policy(paramiko.RejectPolicy())
            endpoint_client.connect(hostname=endpoint_ip, username=endpoint_username, port=22, pkey=pkey)
            
            #getting hash, last modified date and folder/file type before backup runs(will be used for configuration.json)
            command= f"$fileInfo = @{{}}; Get-ChildItem -Path \"{remote_folder}\" -Recurse | ForEach-Object {{ $itemPath = $_.FullName; $itemInfo = @{{'LastModified'=$_.LastWriteTime.ToString('M/d/yyyy HH:mm:ss')}}; if ($_.PSIsContainer) {{ $itemInfo['Type'] = 'Folder' }} else {{ $itemInfo['Type'] = 'File'; $hash = Get-FileHash -Path $_.FullName -Algorithm SHA1 | Select-Object -ExpandProperty Hash; $itemInfo['SHA1Hash'] = $hash }}; $fileInfo[$itemPath] = $itemInfo }}; $fileInfo | ConvertTo-Json"
            _, stdout, stderr = endpoint_client.exec_command(f'powershell.exe -ExecutionPolicy Bypass -Command "{command}"', timeout=60)
            output = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()
            
            file_info = json.loads(output)
            job_name =  fetched_schedule.existing_job.name
            schedule_created_date =  fetched_schedule.created.strftime("%Y-%m-%d_%H-%M-%S")
            archive_queue =  fetched_schedule.archive_queue
            modded_files=[]
            next_increment_config= {}

            #handes the indentification of fullcopy/incremental copy labels
            if archive_queue != '[]' and archive_queue:
                config_file_path= os.path.join("backend", "configurations", f"{job_name}_{schedule_created_date}_next_increment.json")
                if os.path.exists( config_file_path):
                    with open(config_file_path, 'r') as f:
                        stored_increment_content = json.load(f)
                    for path, metainfo in file_info.items():
                        parent_dir = os.path.dirname(path)
                        if parent_dir in file_info:
                            continue
                        if path in stored_increment_content:
                            if metainfo.get('Type') == 'File':
                                if metainfo.get('SHA1Hash') != stored_increment_content[path]['SHA1Hash']  or metainfo.get('LastModified') != stored_increment_content.get('LastModified'):
                                    next_increment_config[path] = metainfo
                                    modded_files.append(path.replace("\\\\", "/")) #handles path nuances
                            elif metainfo.get('Type') == 'Folder':
                                if metainfo['LastModified'] != stored_increment_content[path].get('LastModified'):
                                    modded_files.append(path.replace("\\\\", "/"))
                                    next_increment_config[path] = metainfo
                    modded_files.insert(0, 'incremental paths')
                    with open(config_file_path, 'w') as wf:
                        json.dumps(next_increment_config, wf, indent=4)
        
                else:
                    with open(config_file_path, "w") as f:
                        json.dump(file_info, f, indent=4)
            else:
                config_file_path= os.path.join("backend", "configurations", f"{job_name}_{schedule_created_date}_full.json")
                with open(config_file_path, "w") as f:
                    json.dump(file_info, f, indent=4)

                for path, metainfo in file_info.items():
                    parent_dir = os.path.dirname(path)
                    if parent_dir in file_info:
                        continue
                    modded_files.append(path.replace("\\\\", "/"))
                modded_files.insert(0, remote_folder_name)
            threading.Thread(target=Zeroapi.run_backup_thread, args=(storage_client, endpoint_username, endpoint_ip, selected_storage_volumes, job_id, sch_id, modded_files)).start()
            
            job = scheduler.get_job(f"{job_id}:{sch_id}")
            if job:
                trigger_type= job.trigger.__class__.__name__
                if trigger_type == "CronTrigger":
                    next_backup_time = job.next_run_time
                    fetched_schedule.next_sch_datetime = next_backup_time
                    db.session.commit() 
            else:
                fetched_schedule = ScheduledJob.query.filter_by(id=sch_id).first()
                db.session.delete(fetched_schedule)
                db.session.flush()
                db.session.delete(fetched_schedule.existing_job)
                db.session.commit() 
        
    #gets restore points based on satus of archive queue, returns in friendly format
    @app.route('/zeroapi/v1/backup/get_restore_points/<job_id>', methods=['GET'])
    def get_restore_points(job_id):
        user_token= request.headers['Authorization'].split(' ')[1]
        if not user_token:
            return jsonify({"message": "Access token is missing or invalid"}),401
        try:
            decoded = jwt.decode(user_token, app.config['SECRET_KEY'], algorithms=['HS256'])
            namepart= decoded['sub'].lower()
            fetched_user = User.query.filter_by(username=namepart).first()
            if namepart == fetched_user.username.lower():
                fetched_schedule = ScheduledJob.query.filter_by(job_id=job_id).first()
                if fetched_schedule:
                    archive_queue_str = fetched_schedule.archive_queue
                    archive_queue = ast.literal_eval(archive_queue_str)
                    restore_point_labels={}
                    for archive_label in archive_queue: 
                        datetime_part = " ".join(archive_label.split("_")[1:])
                        datetime_object = datetime.strptime(datetime_part, '%Y-%m-%d %H-%M-%S')
                        restore_point_label = datetime_object.strftime('%Y-%m-%d %I:%M:%S%p')
                        restore_point_labels[archive_label] = restore_point_label
                        #restore_point_labels.append({archive_label: restore_point_label})
                    return jsonify(restore_point_labels),200
                else:
                    return jsonify({"response":  []}),200
        except Exception as e:
            print(e)
            return jsonify({"response":  -1}),500
    
    
    #handles restoration, merging of full copies and increments
    @app.route('/zeroapi/v1/restore', methods=['POST'])
    def restore():
        user_token= request.headers['Authorization'].split(' ')[1]
        if not user_token:
            return jsonify({"message": "Access token is missing or invalid"}),401
        try:
            decoded = jwt.decode(user_token, app.config['SECRET_KEY'], algorithms=['HS256'])
            namepart= decoded['sub'].lower()
            fetched_user = User.query.filter_by(username=namepart).first()
            if namepart == fetched_user.username.lower():
                data = request.get_json()
                restore_point = data.get("restore_point")
                job_id = data.get("job_id")
                fetched_schedule = ScheduledJob.query.filter_by(job_id=job_id).first()
                archive_str=''
                if fetched_schedule:
                    archive_queue_str = fetched_schedule.archive_queue
                    archive_queue= ast.literal_eval(archive_queue_str)
                    if restore_point in archive_queue:
                        restore_point_index = archive_queue.index(restore_point)
                        increment_list = archive_queue[:restore_point_index+1]
                        zcryptobj= ZeroCryptor()
                        #handles the transfer of each increments and merging with full copy
                        for increment in increment_list:
                            endpoint_user = fetched_schedule.existing_endpoint.username
                            endpoint_ip_digest = fetched_schedule.existing_endpoint.ip
                            endpoint_ip = zcryptobj._decrypt_data(encrypted_data= endpoint_ip_digest, type="ENDPOINT")

                            storage_user = fetched_schedule.existing_job.esn_pair.storage_node.username
                            storage_ip_digest= fetched_schedule.existing_job.esn_pair.storage_node.ip
                            storage_ip = zcryptobj._decrypt_data(encrypted_data= storage_ip_digest, type="STORAGE")


                            pkey = paramiko.RSAKey.from_private_key_file(app.config.get('Z_KEY_PATH'))
                            storage_client = paramiko.SSHClient()
                            storage_client.load_system_host_keys()
                            storage_client.set_missing_host_key_policy(paramiko.RejectPolicy())
                            storage_client.connect(hostname=storage_ip, username=storage_user, port=22, pkey=pkey)
                            command =  f'sftp -oBatchMode=yes -C {endpoint_user}@{endpoint_ip}'
                            stdin, stdout, stderr = storage_client.exec_command(command)
                            #tbd handle the merging of increments on endpoint, the following only restore the full copy
                            restore_commands = [f'put -r "D:/{restore_point}" "C:/Users/Administrator/" ','bye']
                            for cmd in restore_commands:
                                stdin.write(cmd + "\n")
                                stdin.flush()
                                time.sleep(0.5)  

                            stdin.close()  
                            stdin.write("bye\n")
                            stdin.flush()
                            stdin.close()
                            error = stderr.read().decode().strip()
                            output = stdout.read().decode().strip()
                            sftp_exit_code = stdout.channel.recv_exit_status()








        except Exception as e:
            print(e)
            return jsonify({"response":  -1}),500
        
    
    @staticmethod
    def remove_sch_job(sch_job_id):
        scheduler.remove_job(sch_job_id)

    @staticmethod
    def remove_all_sch_jobs():
        jobs = scheduler.get_jobs()
        for job in list(jobs):  
            print(f"  Removing job with ID: {job.id}")
            scheduler.remove_job(job.id)
        print("All jobs have been removed.")