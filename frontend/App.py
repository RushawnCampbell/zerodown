from tkinter import *
import customtkinter as gui
from frontend.LoginView import LoginView
from frontend.HomeView import HomeView
from frontend.EndpointRegistration import EndpointRegistration
from frontend.components.ToolBar import ToolBar
from PIL import Image, ImageTk

class App(gui.CTk):
    def __init__(self):
        super().__init__()
        self.configure(bg_color="red")
        self.title("ZeroDown: Backup & Restoration Solution")
        self.grid_columnconfigure(0, weight=1) 
        self.grid_rowconfigure(0, weight=1) 
        self.grid_rowconfigure(1, weight=0) 
        self.set_window_position(400,200)

        try:
            # window icon path
            icon_image = Image.open("./frontend/assets/icons/zerodown.png") # Use a .png file!
            icon_photo = ImageTk.PhotoImage(icon_image)

            # Setting the icon for the Tk window (root)
            self.wm_iconphoto(True, icon_photo)  # For Tkinter
        
            self.iconbitmap("./frontend/assets/icons/zerodown.ico") # For .ico files (Windows only)
            
            #self.iconbitmap(default="path/to/your/icon.xbm") # For .xbm files (Linux)

        except Exception as e:
            print(f"Error setting icon: {e}")  # Handle potential errors


        self.home_view = None
        self.backup_view = None  # Initialize to None
        self.restore_view = None
        self.endpoint_reg_view = None
        self.tool_bar= ToolBar(self)
        self.tool_bar.grid_forget()
        self.login_view = LoginView(self)
        

    
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
        self.login_view.grid_forget()  # Hide login view
        self.home_view = HomeView(self)

    def show_endpoint_registration(self):
        self.title("ZeroDown: Endpoint Registration")
        #self.set_window_position(800,600)
        self.home_view.pack_forget()  # Hide login view
        self.endpoint_reg_view = EndpointRegistration(self)
        self.endpoint_reg_view.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")


    """def show_backup_view(self, user_id):
        self.login_view.pack_forget()  # Hide login view

        self.backup_view = BackupView(self, user_id)
        self.backup_view.pack(fill="both", expand=True)

        self.restore_view = RestoreView(self, user_id)  # Initialize restore view
        self.restore_view.pack(fill="both", expand=True)  # Show it initially"""

        # switching between backup and restore views later
        # switch_to_restore_button = ctk.CTkButton(self, text="Switch to Restore", command=self.show_restore_view)
        # switch_to_restore_button.pack()
        

    # function to switch to restore view (we will implement switch back later)
    # def show_restore_view(self):
    #     self.backup_view.pack_forget()
    #     self.restore_view.pack(fill="both", expand=True)
