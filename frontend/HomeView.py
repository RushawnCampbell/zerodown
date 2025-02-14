import customtkinter as gui
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil  # For file operations (backup/restore)
from PIL import Image, ImageTk

class HomeView(gui.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="#2B2B2B")
        """self.grid(row=0, column=0, padx=0, pady=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)"""


        self.grid_columnconfigure(0, weight=1)  

        self.label_frame = gui.CTkFrame(self)
        self.label_frame.grid(row=0, column=0, padx=40, pady=0, sticky="nsew")
        self.label_frame.configure(fg_color="#2B2B2B")
       

        self.home_label = gui.CTkLabel(self.label_frame, 
                                       text="Welcome User",
                                       font=gui.CTkFont(size=30, weight="bold"),  # Large font
                                       wraplength=700,  # Adjust wraplength as needed
                                       justify="center")  # Center the text
        self.home_label.pack(pady=0, padx=0, fill="x") #fill x to make label expand horizontally


        self.button_frame = gui.CTkFrame(self)
        self.button_frame.grid(row=1, column=0, padx=40, pady=20) # Add padding
        self.button_frame.configure(fg_color="#000000")

        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=1)
        self.button_frame.grid_columnconfigure(3, weight=1)


        image = Image.open("./frontend/assets/icons/computer.png")
        self.ctk_image1 = gui.CTkImage(light_image=image, dark_image=image, size=(50, 50))
        self.button1 = gui.CTkButton(self.button_frame, image=self.ctk_image1,text=" Register \n Endpoint",)
        self.button1.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        

        image2 = Image.open("./frontend/assets/icons/database.png")
        self.ctk_image2 = gui.CTkImage(light_image=image2, dark_image=image2, size=(50, 50))
        self.button2 = gui.CTkButton(self.button_frame, image=self.ctk_image2, text=" Register \n Storage Node")
        self.button2.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        image3 = Image.open("./frontend/assets/icons/recover.png")
        self.ctk_image3 = gui.CTkImage(light_image=image3, dark_image=image3, size=(50, 50))
        self.button3 = gui.CTkButton(self.button_frame, image=self.ctk_image3, text=" Recover \n Endpoint")
        self.button3.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        image4 = Image.open("./frontend/assets/icons/backup.png")
        self.ctk_image4 = gui.CTkImage(light_image=image4, dark_image=image4, size=(50, 50))
        self.button4 = gui.CTkButton(self.button_frame, image=self.ctk_image4, text="Create \n Backup")
        self.button4.grid(row=0, column=3, padx=10, pady=10, sticky="ew")



    """def browse_source(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.source_entry.delete(0, gui.END)  # Clear current text
            self.source_entry.insert(0, folder_path)

    def browse_destination(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.destination_entry.delete(0, gui.END)
            self.destination_entry.insert(0, folder_path)

    def perform_backup(self):
        source = self.source_entry.get()
        destination = self.destination_entry.get()

        if not source or not destination:
            self.show_message("Error", "Please select both source and destination folders.")
            return

        try:
            # Basic backup (copy the entire directory)
            shutil.copytree(source, destination, dirs_exist_ok=True) # Overwrites if dest exists
            self.set_status("Backup Complete")
            self.show_message("Success", "Backup completed successfully!")

        except Exception as e:
            self.set_status(f"Backup Failed: {e}")
            self.show_message("Error", f"Backup failed: {e}")

    def perform_restore(self):
        source = self.source_entry.get()
        destination = self.destination_entry.get()

        if not source or not destination:
            self.show_message("Error", "Please select both source and destination folders.")
            return

        if not os.path.exists(source):  # Check if the source (backup) exists
            self.show_message("Error", "Backup folder not found.")
            return

        try:
            shutil.copytree(source, destination, dirs_exist_ok=True)
            self.set_status("Restore Complete")
            self.show_"""