import customtkinter as gui
import tkinter as tk
import os, requests
from frontend.components.Popup import Popup
from PIL import Image

class JobStatus(Popup):
    def __init__(self, master, title, total_storage_volumes, job_id):
        super().__init__(master, title)
        self.total_storage_volumes = total_storage_volumes
        self.job_id = job_id
        self.master = master
        self.status_label= None
        self.configure_body()
        

    def configure_body(self):
        self.configure(fg_color="#FFFFFF")
        self.protocol("WM_DELETE_WINDOW", self.disable_close)

        self.rowconfigure(0, weight=1) 

        main_frame = gui.CTkFrame(self, fg_color="transparent") 
        main_frame.pack(expand=True) 

        gif_label = gui.CTkLabel(main_frame, text="")
        gif_label.pack(pady=(0, 5)) 

        self.status_label = gui.CTkLabel(main_frame, text= f"Backing up to 1 of {self.total_storage_volumes} Storage Node ")
        self.status_label.pack(pady=(5, 0)) 
        self.status_label.configure(text_color="#1fa59d")

        gif_path = os.path.join("frontend", "assets", "images", "testing.gif")
        self.display_gif(gif_label, gif_path, 100, 100)

        self.close_button = gui.CTkButton(self, text="Close(Backup will continue to run)", command=self.on_close)
        self.close_button.configure(state="disabled", fg_color="#1fa59d")
        self.close_button.grid(row=3, column=0, pady=20) 