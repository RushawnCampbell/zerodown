from .  import app, db, login_manager
from flask import request, jsonify, send_file
from flask_login import login_user, logout_user, current_user, login_required
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
                login_user(user)
                tokencreationtime = datetime.now(timezone.utc).strftime("%H:%M:%S")
                token  = jwt.encode({'sub':uname,'initime': tokencreationtime}, app.config.get('SECRET_KEY'),algorithm='HS256')
                    
                return jsonify({
                    "message": "Login Successful",
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "user_id": user.user_id,
                    "token": token
                }),200
            else:
                return jsonify({
                    "message": "Login failed, check your username and password then try again.",
                }),401


    
    @app.route('/zeroapi/v1/logout', methods=['GET'])
    @login_required
    def logout():
            if request.method == 'GET':
                logout_user()
                return jsonify({
                    "message": "Log out successful"
                }),200
            

    @app.route('/zeroapi/v1/download/<download_type>', methods=['GET'])
    @login_required
    def download(download_type):
        try:
            filename = f'{download_type}.exe'
            file_path = os.path.join("dist", filename) 
            if not os.path.exists(file_path):
                return jsonify({
                    "message": "The requested resource could not be found. Contact the ZeroDown Support for help.",
                }),404
            return send_file(
                file_path,
                as_attachment=True,
                download_name=filename  # Sets the filename in the user's download
            )
        except FileNotFoundError:
            return "File not found", 404
        except Exception as e:
            return f"An error occurred: {e}", 500

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)



