import customtkinter as gui, traceback, json, requests, tkinter as tk
from PIL import Image
from frontend.components.RemoteExplorer import RemoteExplorer
from frontend.components.JobStatus import JobStatus
from frontend.components.ScheduleJob import ScheduleJob

class Menu(gui.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master.title("ZeroDown: Main Menu")
        self.grid(row=0, column=0, padx=100, pady=100, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Menu items frame will expand

        # Title Label
        self.title_label = gui.CTkLabel(self, text="ZeroDown Menu", font=gui.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        # Menu Items Frame
        self.menu_items_frame = gui.CTkFrame(self)
        self.menu_items_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.menu_items_frame.grid_columnconfigure(0, weight=1) # Center buttons

        button_width = 25

        # Buttons in Menu Items Frame
        self.manage_endpoints_button = gui.CTkButton(self.menu_items_frame, text="Manage Endpoints", width=button_width, command=lambda viewclassname='endpointmanagement' : self.master.show_view(viewclassname))
        self.manage_endpoints_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.manage_storage_nodes_button = gui.CTkButton(self.menu_items_frame, text="Manage Storage Nodes", width=button_width)
        self.manage_storage_nodes_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.reset_tracking_button = gui.CTkButton(self.menu_items_frame, text="Manage Scheduled Jobs", width=button_width)
        self.reset_tracking_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        self.view_logs_button = gui.CTkButton(self.menu_items_frame, text="Reset All Storage Tracking ", width=button_width)
        self.view_logs_button.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

        self.contact_support_button = gui.CTkButton(self.menu_items_frame, text="View Logs", width=button_width)
        self.contact_support_button.grid(row=4, column=0, padx=5, pady=5, sticky="ew")

        # Close Button (at the bottom of the parent frame)
        self.close_button = gui.CTkButton(self, text="Close Menu", command=self.master.hide_menu)
        self.close_button.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="ew")
        self.grid_rowconfigure(3, weight=0) # Ensure the close button stays at the bottom