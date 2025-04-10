import customtkinter as gui, ipaddress, requests, tkinter as tk
from frontend.components.SetupDownloader import SetupDownloader
from frontend.components.TestConnection import TestConnection
from PIL import Image
class Restoration(gui.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(padx=20, pady=20, fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        title_label = gui.CTkLabel(self, text="Create Backup Job", font=gui.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(10, 20), sticky="ew")

        description_label = gui.CTkLabel(self, text="Backup Description")
        description_label.grid(row=1, column=0, padx=(20, 5), pady=(5, 5), sticky="w")

        self.description_entry = gui.CTkEntry(self)
        self.description_entry.grid(row=2, column=0, padx=(20, 5), pady=(5, 5), sticky="ew")

        endpoint_label = gui.CTkLabel(self, text="Select Endpoint")
        endpoint_label.grid(row=1, column=1, padx=(5, 5), pady=(5, 5), sticky="w")

        endpoint_options = ["Endpoint 1", "Endpoint 2", "Endpoint 3"]  # Replace with actual options
        self.endpoint_dropdown = gui.CTkComboBox(self, values=endpoint_options)
        self.endpoint_dropdown.grid(row=2, column=1, padx=(5, 5), pady=(5, 5), sticky="ew")

        backup_type_label = gui.CTkLabel(self, text="Select Backup Type")
        backup_type_label.grid(row=1, column=2, padx=(5, 20), pady=(5, 5), sticky="w")

        backup_type_options = ["Full", "Incremental", "Differential"] 
        self.backup_type_dropdown = gui.CTkComboBox(self, values=backup_type_options)
        self.backup_type_dropdown.grid(row=2, column=2, padx=(5, 20), pady=(5, 5), sticky="ew")

        # Row 2: Browse Items
        browse_items_button = gui.CTkButton(self, text="Browse Items")
        browse_items_button.grid(row=3, column=0, columnspan=3, pady=(10, 5), padx=20, sticky="ew")

        # Row 3: Storage Node, Browse Destination
        storage_node_label = gui.CTkLabel(self, text="Select Storage Node")
        storage_node_label.grid(row=4, column=0, padx=(20, 5), pady=(5, 5), sticky="w")

        storage_node_options = ["Node A", "Node B", "Node C"]  
        self.storage_node_dropdown = gui.CTkComboBox(self, values=storage_node_options)
        self.storage_node_dropdown.grid(row=5, column=0, padx=(20, 5), pady=(5, 5), sticky="ew")

        browse_destination_button = gui.CTkButton(self, text="Browse Destination")
        browse_destination_button.grid(row=5, column=1, padx=(5, 20), pady=(5, 5), sticky="ew", columnspan=2)

        # Row 4: Backup Now, Schedule Backup
        backup_now_button = gui.CTkButton(self, text="Backup Now")
        backup_now_button.grid(row=6, column=0, padx=(20, 5), pady=(10, 20), sticky="ew")

        schedule_backup_button = gui.CTkButton(self, text="Schedule Backup")
        schedule_backup_button.grid(row=6, column=1, padx=(5, 20), pady=(10, 20), sticky="ew", columnspan=2)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)