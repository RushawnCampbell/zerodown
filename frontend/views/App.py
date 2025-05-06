from tkinter import *
import tkinter as tkint
import os, platform, keyring, getpass
import customtkinter as gui
from frontend.views.Loginview import Loginview
from frontend.views.Homeview import Homeview
from frontend.views.Endpointregistration import Endpointregistration
from frontend.views.Endpointmanagement import Endpointmanagement
from frontend.views.Storageregistration import Storageregistration
from frontend.views.Storagemanagement import Storagemanagement
from frontend.views.Scheduledjobs import Scheduledjobs
from frontend.views.Backupjob import Backupjob
from frontend.components.Menu import Menu
from frontend.Utility.CommonMethods import CommonMethods

import sys

from frontend.components.ToolBar import ToolBar
from PIL import Image, ImageTk

class App(gui.CTk):
    def __init__(self):
        super().__init__()
        self.app_name="ZeroDown"
        self.title("ZeroDown: Backup & Restoration Solution")
        self.windows_user= self.get_windows_username()
        self.configure(bg_color="red")
        self.grid_columnconfigure(0, weight=1) 
        self.grid_rowconfigure(0, weight=1) 
        self.grid_rowconfigure(1, weight=0) 
        self.set_window_position(400,200)
        self.set_icon()

        self.homeview = None
        self.backupjob = None  
        self.restoreview = None
        self.endpointregistration = None
        self.endpointmanagement = None
        self.storagemanagement = None
        self.storageregistration = None
        self.scheduledjobs = None
        self.current_body_widget = None
        self.current_body_widget_name= None
        self.widget_str = None
        self.menu= None
        self.tool_bar= ToolBar(self)
        self.tool_bar.grid_forget()

        self.loginview = Loginview(self)
        

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
        x = (screen_width - window_width) // 2  
        y = (screen_height - window_height) // 2  

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.resizable(width=False, height=False)


    def set_window_position_top_centered(self, window_width, window_height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = 0  

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.resizable(width=False, height=False)

    def route_home(self):
        try:
            self.current_body_widget = self.grid_slaves(row=0)
            if self.current_body_widget:
                self.current_body_widget = self.current_body_widget[0]
                setattr(self, "current_body_widget_name", self.current_body_widget.__class__.__name__ )

                if self.current_body_widget.__class__.__name__ == "Homeview":
                    return

                elif self.current_body_widget.__class__.__name__ == "Menu":
                    self.menu.grid_forget()
                    if self.homeview == None:
                        self.set_window_position_top_centered(850,680)
                        self.homeview = Homeview(self)
                        return
                    else:
                        self.title("ZeroDown: Home")
                        self.homeview.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
                        return

                else:
                    if self.homeview == None:
                        self.set_window_position_top_centered(850,680)
                        self.homeview = Homeview(self)
                        return
                    getattr(self, self.current_body_widget_name.lower()).destroy()
                    setattr(self, self.current_body_widget_name.lower(), None)
                    self.title("ZeroDown: Home")
                    self.homeview.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
                    return
            else:
                return
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            line_number = exc_traceback.tb_lineno
            print(f"An exception occurred: {e}")
            print(f"Line number: {line_number}")
            tkint.messagebox.showerror("Render Error", "An Error Occurred While Rendering This Screen")


    def show_menu(self):
        self.current_body_widget = self.grid_slaves(row=0)
        if self.current_body_widget:

            self.current_body_widget =  self.current_body_widget[0]
            self.current_body_widget_name = self.current_body_widget.__class__.__name__.lower()
            
            if self.current_body_widget_name == "menu":
                self.title("ZeroDown: Main Menu")
                return
            
            tkinterstring = f"self.{self.current_body_widget_name}.grid_forget()"
            eval(tkinterstring)
        
            if self.menu == None:
                self.menu = Menu(self)
                self.widget_str =  f"self.{self.current_body_widget_name}"
            else:
                self.title("ZeroDown: Main Menu")
                self.menu.grid(row=0, column=0, padx=100, pady=100, sticky="nsew")
                self.widget_str= f"self.{self.current_body_widget_name}"


    def hide_menu(self):
        self.menu.grid_forget()
        if eval(self.widget_str) == None:
            new_widget_obj_str = self.current_body_widget_name.title()
            eval(f"{new_widget_obj_str}.(self)")
        else:
            eval(f"{self.widget_str}.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')")


    def show_view(self, viewclassname):
        try:
            self.current_body_widget = self.grid_slaves(row=0)
            if self.current_body_widget:

                self.current_body_widget =  self.current_body_widget[0]
                self.current_body_widget_name = self.current_body_widget.__class__.__name__.lower()
            
                if getattr(self, "current_body_widget_name") == 'homeview':
                    self.homeview.grid_forget()
                elif getattr(self, "current_body_widget_name") == 'menu':
                    self.menu.grid_forget()
                else:
                    getattr(self, f"{self.current_body_widget_name}").destroy()
                    setattr(self, f"{self.current_body_widget_name}", None) 

                if getattr(self, viewclassname) == None:
                    if viewclassname == "endpointregistration":
                        self.endpointregistration  = Endpointregistration(self, 'Endpoint')

                    elif viewclassname == "storageregistration":
                        self.storageregistration  = Storageregistration(self, 'Endpoint')

                    else:
                        tkinterstring = f"{viewclassname.title()}(self)"
                        setattr(self, viewclassname, eval(tkinterstring) )
                else:
                
                    getattr(self, viewclassname).grid(row=0, column=0, padx=20, pady=20, sticky='nsew')
        except Exception as e:
            tkint.messagebox.showerror("Render Error", "An Error Occurred While Rendering This View. Please Report To ZeroDown Support If It Reoccurrs.")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            line_number = exc_traceback.tb_lineno
            print(f"An exception occurred: {e}")
            print(f"Line number: {line_number}")


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
            
            token = CommonMethods.get_token(self.app_name, self.windows_user)
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


    