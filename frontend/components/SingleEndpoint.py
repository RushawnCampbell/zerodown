import customtkinter
from frontend.components.Popup import Popup

class SingleEndpoint(Popup):

    def __init__(self, master, title):
        super().__init__(master, title)

        self.configure(fg_color="#2B2B2B")

        self.after(300,self.set_window_position_top_centered, 600, 700)

        self.initial_scheduled_jobs = ["Job Alpha", "Job Beta", "Job Gamma"]
        self.initial_paired_nodes = ["Storage Node X", "Storage Node Y", "Storage Node Z"]

        self.ip_address_label = customtkinter.CTkLabel(self, text="IP Address", text_color="white")
        self.ip_address_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.ip_address_entry = customtkinter.CTkEntry(self, fg_color="white", text_color="black")
        self.ip_address_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.update_ip_button = customtkinter.CTkButton(self, text="Update", state="disabled")
        self.update_ip_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")


        self.backup_user_label = customtkinter.CTkLabel(self, text="Authorized Backup User", text_color="white")
        self.backup_user_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.backup_user_entry = customtkinter.CTkEntry(self, fg_color="white", text_color="black")
        self.backup_user_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.update_backup_button = customtkinter.CTkButton(self, text="Update", state="disabled")
        self.update_backup_button.grid(row=1, column=2, padx=10, pady=10, sticky="e")

        self.scheduled_jobs_frame = customtkinter.CTkScrollableFrame(self, label_text="Active Scheduled Jobs", fg_color="black", label_text_color="white")
        self.scheduled_jobs_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        self._populate_scheduled_jobs()

    
        self.paired_nodes_frame = customtkinter.CTkScrollableFrame(self, label_text="Associated Storage Nodes", fg_color="black", label_text_color="white")
        self.paired_nodes_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        self._populate_paired_nodes()

        self.close_button = customtkinter.CTkButton(self, text="Close", command=self.on_close)
        self.close_button.grid(row=4, column=0, columnspan=3, padx=10, pady=(10, 10), sticky="ew")

        self.grid_columnconfigure(1, weight=1) 

    def _populate_scheduled_jobs(self):
        for i, job_name in enumerate(self.initial_scheduled_jobs):
            job_label = customtkinter.CTkLabel(self.scheduled_jobs_frame, text=job_name, text_color="white")
            job_label.grid(row=i, column=0, padx=(20, 5), pady=5, sticky="w")
            remove_button = customtkinter.CTkButton(self.scheduled_jobs_frame, text="Remove")
            remove_button.grid(row=i, column=1, padx=(5, 5), pady=5, sticky="e")
            restore_button = customtkinter.CTkButton(self.scheduled_jobs_frame, text="Restore from this Job")
            restore_button.grid(row=i, column=2, padx=(5, 20), pady=5, sticky="e")
            self.scheduled_jobs_frame.grid_columnconfigure(1, weight=1) # Ensure buttons don't overlap if window is narrow

    def _populate_paired_nodes(self):
        for i, node_name in enumerate(self.initial_paired_nodes):
            node_label = customtkinter.CTkLabel(self.paired_nodes_frame, text=node_name, text_color="white")
            node_label.grid(row=i, column=0, padx=(20, 10), pady=5, sticky="w")
            unpair_button = customtkinter.CTkButton(self.paired_nodes_frame, text="Unpair")
            unpair_button.grid(row=i, column=1, padx=(10, 20), pady=5, sticky="e")