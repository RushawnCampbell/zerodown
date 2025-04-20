import customtkinter as gui
from PIL import Image
from tkinter import messagebox
from frontend.components.RestoreJob import RestoreJob
import datetime
import textwrap

class HomeView(gui.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.master = master
        self.configure(fg_color="#2B2B2B")
        self.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=0) # For the recent jobs label
        self.grid_rowconfigure(1, weight=1) # For the recent jobs frame
        self.grid_rowconfigure(2, weight=0) # For the storage info label
        self.grid_rowconfigure(3, weight=1) # For the storage info frame
        self.grid_rowconfigure(4, weight=0) # For the button frame

        self.grid_columnconfigure(0, weight=1)

        # Recent Events Label
        self.recent_label = gui.CTkLabel(self, text="Recent Events", font=gui.CTkFont(size=16, weight="bold"), anchor="w")
        self.recent_label.grid(row=0, column=0, padx=40, pady=(20, 2), sticky="ew")

        self.recent_frame = gui.CTkScrollableFrame(self, width=850, height=80) # Further reduced height
        self.recent_frame.grid(row=1, column=0, padx=40, pady=(2, 2), sticky="ew")
        self.recent_frame.configure(fg_color="#000000")
        self.sample_data = [] # Initialize as empty list
        self.recent_no_data_label = None

        # Storage Nodes Label
        self.storage_label = gui.CTkLabel(self, text="Storage Nodes", font=gui.CTkFont(size=16, weight="bold"), anchor="w")
        self.storage_label.grid(row=2, column=0, padx=40, pady=(8, 2), sticky="ew")

        self.storage_frame = gui.CTkScrollableFrame(self, width=850, height=40) # Further reduced height
        self.storage_frame.grid(row=3, column=0, padx=40, pady=(2, 8), sticky="ew")
        self.storage_frame.configure(fg_color="#202020")
        self.sample_storage_data = [] # Initialize as empty list
        self.storage_no_data_label = None
        self.storage_add_button = None

        self._check_and_populate()

        self.button_frame = gui.CTkFrame(self)
        self.button_frame.grid(row=4, column=0, padx=40, pady=(8, 20), sticky="ew")
        self.button_frame.configure(fg_color="#202020")

        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=1)
        self.button_frame.grid_columnconfigure(3, weight=1)

        image = Image.open("./frontend/assets/icons/computer.png")
        self.ctk_image1 = gui.CTkImage(light_image=image, dark_image=image, size=(50, 50))
        self.button1 = gui.CTkButton(self.button_frame, image=self.ctk_image1, text=" Register \n Endpoint", command=self.master.show_endpoint_registration)
        self.button1.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        image2 = Image.open("./frontend/assets/icons/database.png")
        self.ctk_image2 = gui.CTkImage(light_image=image2, dark_image=image2, size=(50, 50))
        self.button2 = gui.CTkButton(self.button_frame, image=self.ctk_image2, text=" Register \n Storage Node", command=self.master.show_storage_registration)
        self.button2.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        image3 = Image.open("./frontend/assets/icons/backup.png")
        self.ctk_image3 = gui.CTkImage(light_image=image3, dark_image=image3, size=(50, 50))
        self.button3 = gui.CTkButton(self.button_frame, image=self.ctk_image3, text=" Create \n Backup", command=self.master.show_backup_job)
        self.button3.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        image4 = Image.open("./frontend/assets/icons/recover.png")
        self.ctk_image4 = gui.CTkImage(light_image=image4, dark_image=image4, size=(50, 50))
        self.button4 = gui.CTkButton(self.button_frame, image=self.ctk_image4, text="Restore \n Endpoint")
        self.button4.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

    def _check_and_populate(self):
        if not self.sample_data:
            self.recent_no_data_label = gui.CTkLabel(self.recent_frame, text="No Recent Events Yet")
            self.recent_no_data_label.grid(row=0, column=0, padx=20, pady=(25, 25), sticky="ew")
            self.recent_frame.grid_rowconfigure(0, weight=1) # Center vertically
            self.recent_frame.grid_columnconfigure(0, weight=1) # Center horizontally
        else:
            self._populate_recent_frame(self.sample_data)

        if not self.sample_storage_data:
            self.storage_no_data_label = gui.CTkLabel(self.storage_frame, text="You Do Not Have Any Registered Storage Nodes ")
            self.storage_no_data_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="ew")
            self.storage_add_button = gui.CTkButton(self.storage_frame, text="Register Storage Node")
            self.storage_add_button.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")
            self.storage_frame.grid_rowconfigure(0, weight=1) # Center vertically
            self.storage_frame.grid_rowconfigure(1, weight=1) # Center vertically
            self.storage_frame.grid_columnconfigure(0, weight=1) # Center horizontally
        else:
            self._populate_storage_frame(self.sample_storage_data)

    def _populate_recent_frame(self, data_list, row_limit=None):
        # Clear existing widgets in the frame
        for widget in self.recent_frame.winfo_children():
            widget.destroy()

        if data_list:
            description_width = 60 # Character limit before wrapping

            gui.CTkLabel(self.recent_frame, text="Time", font=gui.CTkFont(weight="bold"), anchor="w").grid(row=0, column=0, padx=10, pady=(10, 3), sticky="ew")
            gui.CTkLabel(self.recent_frame, text="Type", font=gui.CTkFont(weight="bold"), anchor="w").grid(row=0, column=1, padx=10, pady=(10, 3), sticky="ew")
            gui.CTkLabel(self.recent_frame, text="Description", font=gui.CTkFont(weight="bold"), anchor="w").grid(row=0, column=2, padx=10, pady=(10, 3), sticky="ew")
            gui.CTkLabel(self.recent_frame, text="Level", font=gui.CTkFont(weight="bold"), anchor="e").grid(row=0, column=3, padx=10, pady=(10, 3), sticky="ew")

            for i, data in enumerate(data_list):
                if row_limit is not None and i >= row_limit:
                    break
                row_num = i + 1
                gui.CTkLabel(self.recent_frame, text=data["time"], anchor="w").grid(row=row_num, column=0, padx=10, pady=2, sticky="ew")
                gui.CTkLabel(self.recent_frame, text=data["type"], anchor="w").grid(row=row_num, column=1, padx=10, pady=2, sticky="ew")

                wrapped_description = textwrap.fill(data["description"], width=description_width)
                gui.CTkLabel(self.recent_frame, text=wrapped_description, anchor="w", justify="left").grid(row=row_num, column=2, padx=10, pady=2, sticky="ew")

                gui.CTkLabel(self.recent_frame, text=data["level"], anchor="e").grid(row=row_num, column=3, padx=10, pady=2, sticky="ew")

            self.recent_frame.grid_columnconfigure(0, weight=1) # Time
            self.recent_frame.grid_columnconfigure(1, weight=1) # Type
            self.recent_frame.grid_columnconfigure(2, weight=3) # Description
            self.recent_frame.grid_columnconfigure(3, weight=1) # Level

    def _populate_storage_frame(self, data_list, row_limit=None):
        # Clear existing widgets in the frame
        for widget in self.storage_frame.winfo_children():
            widget.destroy()

        if data_list:
            gui.CTkLabel(self.storage_frame, text="Storage Node", font=gui.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=(10, 3), sticky="ew")
            gui.CTkLabel(self.storage_frame, text="Used Storage", font=gui.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=(10, 3), sticky="ew")
            gui.CTkLabel(self.storage_frame, text="Available Storage", font=gui.CTkFont(weight="bold")).grid(row=0, column=2, padx=10, pady=(10, 3), sticky="ew")
            gui.CTkLabel(self.storage_frame, text="", font=gui.CTkFont(weight="bold")).grid(row=0, column=3, padx=10, pady=(10, 3), sticky="ew") # For Remove button header
            gui.CTkLabel(self.storage_frame, text="", font=gui.CTkFont(weight="bold")).grid(row=0, column=4, padx=10, pady=(10, 3), sticky="ew") # For Flush SNR button header

            for i, data in enumerate(data_list):
                if row_limit is not None and i >= row_limit:
                    break
                row_num = i + 1
                gui.CTkLabel(self.storage_frame, text=data["Storage Node"]).grid(row=row_num, column=0, padx=10, pady=2, sticky="ew")
                gui.CTkLabel(self.storage_frame, text=data["Used Storage"]).grid(row=row_num, column=1, padx=10, pady=2, sticky="ew")
                gui.CTkLabel(self.storage_frame, text=data["Available Storage"]).grid(row=row_num, column=2, padx=10, pady=2, sticky="ew")
                remove_button = gui.CTkButton(self.storage_frame, text="Remove", width=80, command=lambda node=data["Storage Node"]: self._remove_node(node))
                remove_button.grid(row=row_num, column=3, padx=10, pady=2, sticky="ew")
                flush_snr_button = gui.CTkButton(self.storage_frame, text="Flush SNR", width=80, command=lambda node=data["Storage Node"]: self._flush_snr(node))
                flush_snr_button.grid(row=row_num, column=4, padx=10, pady=2, sticky="ew")

            for i in range(5):
                self.storage_frame.grid_columnconfigure(i, weight=1)

    def _remove_node(self, node_name):
        print(f"Removing node: {node_name}")

    def _flush_snr(self, node_name):
        print(f"Flushing SNR for node: {node_name}")

    def _run_job(self, job_name):
        print(f"Running job: {job_name}")

    def _restore_job(self, job_name):
        response = messagebox.askyesno("Confirmation", "Are you sure you want to restore this backup?")
        if response:
            RestoreJob(self, f"Restoring {job_name}")

    def _manage_job(self, job_name):
        print(f"Managing job: {job_name}")

""" sample_data = [
    {"time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "type": "Backup", "description": "Daily files backup", "level": "Full"},
    {"time": (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"), "type": "Database", "description": "Weekly database dump", "level": "Differential"},
    {"time": (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), "type": "System", "description": "Monthly full system check with a very long description that should wrap within the allocated width", "level": "Informational"},
]
  sample_storage_data = [
    {"Storage Node": "Server A", "Used Storage": "500 GB", "Available Storage": "1 TB"},
    {"Storage Node": "NAS Unit 1", "Used Storage": "2 TB", "Available Storage": "5 TB"},
    {"Storage Node": "Cloud Backup", "Used Storage": "100 GB", "Available Storage": "Unlimited"},
]
"""