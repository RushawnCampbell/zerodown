
from frontend.components.Popup import Popup
import tkinter as tk
from flask import jsonify
import requests

class BrowseStructure(Popup):
    def __init__(self, master, title, endpoint_name, backup_type):
        super().__init__(master, title)
        self.master =master
        self.backup_type = backup_type
        self.endpoint_name = endpoint_name
        self.after(500, self.custom_set_pos)
        self.get_listing(endpoint_name = self.endpoint_name, backup_type=self.backup_type)

    def custom_set_pos(self):
        self.set_window_position(800,600)

    def get_listing(self, endpoint_name, backup_type):
        resource_url= f"http://127.0.0.1:8080/zeroapi/v1/listing/{endpoint_name.lower()}/{backup_type.lower()}"
        auth_token = self.master.master.retrieve_auth_token()
        zeroheaders = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        del auth_token
        try:
            response = requests.get( resource_url, stream=True, headers=zeroheaders)
            response.raise_for_status()
            parent_names = response.json()
            print("NAMES", parent_names)
        except requests.exceptions.RequestException as e:
            tk.messagebox.showerror("Fetch Error", f"Failed to fetch {e}")
            return -1
        except Exception as e:
            tk.messagebox.showerror("Fetch Error", f"An Application Error Occurred, report this to ZeroDown.")
            return -1
    
