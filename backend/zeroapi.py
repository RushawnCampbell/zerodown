from .  import app, db
from flask import request, jsonify, send_file
from werkzeug.security import check_password_hash
from .Sqlmodels.User import User
from .Sqlmodels.Endpoint import Endpoint
from .Sqlmodels.StorageNode import StorageNode
from .Sqlmodels.ZeroCryptor import ZeroCryptor
import os,jwt, logging, json, paramiko
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
                    filename = f'{download_type}.exe'
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
                    username=data.get('endpoint_user')
                    pkey = paramiko.RSAKey.from_private_key_file(app.config.get('Z_KEY_PATH'))
                    
                    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
                    client = paramiko.SSHClient()
                    client.load_system_host_keys()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
                    client.connect(hostname=hostname, username=username,  pkey=pkey)
                    client.close()
                    del pkey
                    return jsonify({"message": "Successful Connection"}),200
                except Exception as e:
                    return jsonify({
                            "message": "Something went wrong. Contact the ZeroDown Support for help.",
                        }),500
            else:
                return jsonify({"message": "Access token is missing or invalid"}),401

        except Exception as e:
            return jsonify({"message": "Access token is missing or invalid"}),401
        


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
                endpoint_name = data.get('name')
                endpoint_ip= data.get('ip')
                endpoint_user=data.get('endpoint_user')
                if register_type == "endpoint":
                    endpoint_object = Endpoint(ip=endpoint_ip, name=endpoint_name, username=endpoint_user)
                    db.session.add(endpoint_object)
                    db.session.commit()
                    fetched_ip = endpoint_object.ip
                    print("ENCRYPTED IP IS", fetched_ip)
                    print("DECRYPTED IP IS", ZeroCryptor._decrypt_data(fetched_ip, "ENDPOINT"))
                    return jsonify({"message": "Endpoint Node Registered"}),200
                if register_type == "storage":
                    storage_object = StorageNode(ip=endpoint_ip, name=endpoint_name, username=endpoint_user,pub_key=None)
                    db.session.add(storage_object)
                    db.session.commit()
                    return jsonify({"message": "Endpoint Node Registered"}),200
            else:
                print ("I AM HERE")
                return jsonify({"message": "Access token is missing or invalid"}),401
        except Exception as e:
            print(e)
            return jsonify({"message": "Access token is missing or invalid"}),401
        



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