import requests, tkinter as tkint
import os, platform, keyring, getpass

class CommonMethods:

    @staticmethod
    def get_token(app_name, windows_user):
        try:
            service_name = app_name
            username = windows_user
            token = keyring.get_password(service_name, username)
            if token:
                return token
            else:
                return None  
        except Exception as e:
            return None  

    @staticmethod
    def get_objects(obj_type, app_name, windows_user):
        resource_url= f"http://127.0.0.1:8080/zeroapi/v1/objects/{obj_type}"
        auth_token = CommonMethods.get_token(app_name, windows_user)
        zeroheaders = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        del auth_token
        try:
            response = requests.get( resource_url, stream=True, headers=zeroheaders)
            response.raise_for_status()
            object_names = response.json()
            return object_names["response"]
        except requests.exceptions.RequestException as e:
            print ("ERROR IS REQUESTS", e)
            return None
        except Exception as e:
            print ("ERROR IS", e)
            return None