from tkinter import *
import tkinter as tkint
import os, platform, keyring, getpass
import customtkinter as gui
from frontend.LoginView import LoginView
from frontend.HomeView import HomeView
from frontend.EndpointRegistration import EndpointRegistration
from frontend.StorageRegistration import StorageRegistration
from frontend.BackupJob import BackupJob

from frontend.components.ToolBar import ToolBar
from PIL import Image, ImageTk

class App(gui.CTk):
    def __init__(self):
        super().__init__()
        self.app_name="ZeroDown"
        self.windows_user= self.get_windows_username()
        self.configure(bg_color="red")
        self.title("ZeroDown: Backup & Restoration Solution")
        self.grid_columnconfigure(0, weight=1) 
        self.grid_rowconfigure(0, weight=1) 
        self.grid_rowconfigure(1, weight=0) 
        self.set_window_position(400,200)

        self.set_icon()

        self.home_view = None
        self.backup_view = None  # Initialize to None
        self.restore_view = None
        self.endpoint_reg_view = None
        self.tool_bar= ToolBar(self)
        self.tool_bar.grid_forget()
        self.login_view = LoginView(self)

    def set_icon(self):
        try:
            icon_path_png = os.path.join("frontend", "assets", "icons", "zerodown.png")
            icon_path_ico = os.path.join("frontend", "assets", "icons", "zerodown.ico")

            if os.path.exists(icon_path_png):
                icon_image = Image.open(icon_path_png)
                icon_photo = ImageTk.PhotoImage(icon_image)
                self.wm_iconphoto(True, icon_photo)

            if platform.system() == "Windows" and os.path.exists(icon_path_ico):
                self.iconbitmap(icon_path_ico)

        except Exception as e:
            print(f"Error setting icon: {e}")
    
    
    def set_window_position(self, window_width, window_height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2  # Center horizontally
        y = (screen_height - window_height) // 2  # Center vertically

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.resizable(width=False, height=False)

    def route_home(self):
        body_widget = self.grid_slaves(row=0)
        if body_widget:
            widget_to_remove = body_widget[0] 
            widget_to_remove.grid_forget()
            self.home_view.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
            self.title("ZeroDown: Home")

    def show_home_view(self):
        self.title("ZeroDown: Home")
        self.set_window_position(800,600)
        self.login_view.grid_forget()  
        self.home_view = HomeView(self)

    def show_endpoint_registration(self):
        self.title("ZeroDown: Endpoint Registration")
        #self.set_window_position(800,600)
        self.home_view.pack_forget()  
        self.endpoint_reg_view = EndpointRegistration(self, "Endpoint")
        self.endpoint_reg_view.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

    def show_storage_registration(self):
        self.title("ZeroDown: Storage Node Registration")
        #self.set_window_position(800,600)
        self.home_view.pack_forget()  
        self.storage_reg_view = StorageRegistration(self, "Storage Node")
        self.storage_reg_view.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

    def show_backup_job(self):
        self.title("ZeroDown: Create Backup Job")
        #self.set_window_position(800,600)
        self.home_view.pack_forget()  
        self.backup_job_view = BackupJob(self)
        self.backup_job_view.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")


    def get_windows_username(self):
        try:
            username = os.getlogin()
            return username
        except OSError:
            try:
                username = getpass.getuser()
                return username
            except Exception as e:
                print(f"Error getting username: {e}")
                return None

    def store_auth_token(self, zauth_token):
        try:
            service_name = self.app_name
            username = self.windows_user
            keyring.set_password(service_name, username, zauth_token)
        except Exception as e:
            err_msg = str(e)
            tkint.messagebox.showerror("Token Storage Failed", f"Error storing token: {err_msg}")

    def retrieve_auth_token(self):
        try:
            service_name = self.app_name
            username = self.windows_user
            token = keyring.get_password(service_name, username)
            if token:
                return token
            else:
                tkint.messagebox.showerror("Token Retrieval Failed", "Token not found.")
                return None  
        except Exception as e:
            err_msg = str(e)
            tkint.messagebox.showerror("Token Retrieval Failed", f"Error retrieving token: {err_msg}")
            return None  
        
    def delete_auth_token(self):
        try:
            service_name = self.app_name
            username = self.windows_user
            if username:
                keyring.delete_password(service_name, username)
            else:
                tkint.messagebox.showerror("Token Deletion Failed", "Could not determine username.")
        except keyring.errors.PasswordDeleteError: 
            tkint.messagebox.showerror("Token Deletion Failed", "Token not found.")
        except Exception as e:
            err_msg = str(e)
            tkint.messagebox.showerror("Token Deletion Failed", f"Error deleting token: {err_msg}")


    