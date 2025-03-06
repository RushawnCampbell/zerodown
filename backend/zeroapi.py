from .  import app, db, login_manager
from flask import request, jsonify, send_file
from werkzeug.security import check_password_hash
from .Sqlmodels.User import User
import os,json
import jwt
from datetime import datetime, timezone

class Zeroapi:
    @app.route('/zeroapi/v1/adduser', methods=['GET'])
    def adduser():
        newuser  = User(first_name="Rushawn",last_name="Campbell",email="rushawn.campbell@mymona.uwi.edu", username="admin", password="admin123")
        db.session.add(newuser)
        db.session.commit()
        print("status ok user added")
        return jsonify({"stat": "ok user added"})


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
                    "message": "Login Successful",
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "user_id": user.user_id,
                    "zauth_token": token
                }),200
            else:
                return jsonify({
                    "message": "Login failed, check your username and password then try again.",
                }),401


    
    @app.route('/zeroapi/v1/logout', methods=['GET'])
    def logout():
            if request.method == 'GET':
                return jsonify({
                    "message": "Log out successful"
                }),200
            

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
                    print(filename)
                    file_path = os.path.join(app.root_path,"..\\","dist", filename) 
                    print(file_path)
                    print(os.path.isfile(file_path))
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


