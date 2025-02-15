import customtkinter as gui
import os
import shutil  # For file operations (backup/restore)
from PIL import Image


class EndpointRegistration(gui.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.master = master

        self.configure(fg_color="#2B2B2B")
        self.grid_columnconfigure(0, weight=1)  

        self.view_title_frame = gui.CTkFrame(self)
        self.view_title_frame.grid(row=0, column=0, padx=40, pady=0, sticky="nsew")
        self.view_title_frame.configure(fg_color="#2B2B2B")
        self.view_title = gui.CTkLabel(self.view_title_frame, 
                                       text="Register Endpoint ",
                                       font=gui.CTkFont(size=20, weight="bold"),  # Large font
                                       wraplength=700,  # Adjust wraplength as needed
                                       justify="center")  # Center the text
        self.view_title.pack( pady=(0,0), padx=0, fill="x") #fill x to make label expand horizontally

       