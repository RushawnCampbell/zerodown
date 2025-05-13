import customtkinter, requests, json
from frontend.components.Popup import Popup
from frontend.components.RestoreJob import RestoreJob
from frontend.Utility.CommonMethods import CommonMethods
from tkinter import messagebox
import tkinter as tk

class SingleEndpoint(Popup):

    def __init__(self, master, title, endpoint_id):
        super().__init__(master, title)

        self.configure(fg_color="#2B2B2B")
        self.endpoint_id = endpoint_id
        self.restore_points = []

        self.after(300, self.set_window_position_top_centered, 800, 700)

        self.scheduled_jobs_data = []  # Store job dictionaries with id and name
        self.paired_storage_nodes_data = [] # Store storage node dictionaries with id and name

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

        self.paired_nodes_frame = customtkinter.CTkScrollableFrame(self, label_text="Associated Storage Nodes", fg_color="black", label_text_color="white")
        self.paired_nodes_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.close_button = customtkinter.CTkButton(self, text="Close", command=self.on_close)
        self.close_button.grid(row=4, column=0, columnspan=3, padx=10, pady=(10, 10), sticky="ew")

        self.grid_columnconfigure(1, weight=1)

        self.after(500, self._fetch_and_process_endpoint_data)

    def _fetch_and_process_endpoint_data(self):
        endpoint_data = CommonMethods.get_object(
            self.endpoint_id,
            "endpoint",
            self.master.master.app_name,
            self.master.master.windows_user
        )
        if endpoint_data:
            self.ip_address_entry.insert(0, endpoint_data.get("ip", ""))
            self.backup_user_entry.insert(0, endpoint_data.get("authorized_user", ""))
            self.scheduled_jobs_data.extend(endpoint_data.get("scheduled_jobs", []))
            self.paired_storage_nodes_data.extend(endpoint_data.get("storage_nodes", []))
            self._populate_scheduled_jobs()
            self._populate_paired_nodes()

    def _on_remove_job(self, job_id):
        removal_confirmation = messagebox.askyesno(
            "Confirm Endpoint Removal",
            f"Are you sure you want to remove the scheduled job with ID: {job_id}?"
        )
        if removal_confirmation:
            print(f"Remove button clicked for job ID: {job_id}")
            pass

    def get_restore_points(self, job_id):
        resource_url= f"http://127.0.0.1:8080//zeroapi/v1/backup/get_restore_points/{job_id}"
        zauth_token = self.master.master.retrieve_auth_token()
        zeroheaders = {"Authorization": f"Bearer {zauth_token}", "Content-Type": "application/json"}
        del zauth_token
        try:
            response = requests.get( resource_url, stream=True, headers=zeroheaders)
            response.raise_for_status()
            self.restore_points= response.json()["response"]
        except requests.exceptions.RequestException as e:
            tk.messagebox.showerror("Fetch Error", f"Failed to get restore points {e}")
            
        except Exception as e:
            print("ERROR IS",e)
            tk.messagebox.showerror("Fetch Error", f"An Application Error Occurred, report this to ZeroDown.")
        restore_window = RestoreJob(self, "Restore Job", job_id, self.restore_points)

    def _populate_scheduled_jobs(self):
        for widget in self.scheduled_jobs_frame.winfo_children():
            widget.destroy()

        heading_labels = ["Job Name", "Target", "Backup Location", "Actions"]
        for i, heading in enumerate(heading_labels):
            label = customtkinter.CTkLabel(self.scheduled_jobs_frame, text=heading, text_color="white", font=customtkinter.CTkFont(weight="bold"))
            sticky_value = "w" if i == 0 else "ew"  
            padx_left = 20 if i == 0 else 5
            padx_right = 5 if i < len(heading_labels) - 1 else 20
            label.grid(row=0, column=i, padx=(padx_left, padx_right), pady=(5, 5), sticky=sticky_value)
            self.scheduled_jobs_frame.grid_columnconfigure(i, weight=1 if i < len(heading_labels) - 1 else 0) 

        for i, job_data in enumerate(self.scheduled_jobs_data):
            job_name = job_data.get("job_name", "N/A")
            job_id = job_data.get("job_id")
            target_str = job_data.get("target", "{}")
            destination_str = job_data.get("destination", "{}")

            target_volume_keys = "N/A"
            destination_volume_keys = "N/A"

            try:
                target_dict = eval(target_str)
                if "Volumes" in target_dict and isinstance(target_dict["Volumes"], dict):
                    target_volume_keys = ", ".join(target_dict["Volumes"].keys())
            except (SyntaxError, TypeError):
                pass

            try:
                destination_dict = eval(destination_str)
                if "Volumes" in destination_dict and isinstance(destination_dict["Volumes"], dict):
                    destination_volume_keys = ", ".join(destination_dict["Volumes"].keys())
            except (SyntaxError, TypeError):
                pass

            row_num = i + 1 

            job_label = customtkinter.CTkLabel(self.scheduled_jobs_frame, text=job_name, text_color="white")
            job_label.grid(row=row_num, column=0, padx=(20, 5), pady=5, sticky="w")

            target_label = customtkinter.CTkLabel(self.scheduled_jobs_frame, text=target_volume_keys, text_color="white")
            target_label.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")

            destination_label = customtkinter.CTkLabel(self.scheduled_jobs_frame, text=destination_volume_keys, text_color="white")
            destination_label.grid(row=row_num, column=2, padx=5, pady=5, sticky="ew")

            remove_button = customtkinter.CTkButton(self.scheduled_jobs_frame, text="Remove", width=80, command=lambda id=job_id: self._on_remove_job(id))
            remove_button.grid(row=row_num, column=3, padx=(5, 5), pady=5, sticky="e")

            restore_button = customtkinter.CTkButton(self.scheduled_jobs_frame, text="Restore", width=80, command=lambda id=job_id: self.get_restore_points(id))
            restore_button.grid(row=row_num, column=4, padx=(5, 20), pady=5, sticky="e")

        self.scheduled_jobs_frame.grid_columnconfigure(0, weight=1)
        self.scheduled_jobs_frame.grid_columnconfigure(1, weight=1) 
        self.scheduled_jobs_frame.grid_columnconfigure(2, weight=1) 
        self.scheduled_jobs_frame.grid_columnconfigure(3, weight=0) 
        self.scheduled_jobs_frame.grid_columnconfigure(4, weight=0) 


    def _on_unpair_node(self, node_id):
        print(f"Unpair button clicked for storage node ID: {node_id}")
        

    def _populate_paired_nodes(self):
        for widget in self.paired_nodes_frame.winfo_children():
            widget.destroy()
        for i, node_data in enumerate(self.paired_storage_nodes_data):
            node_name = node_data.get("storage_name", "N/A")
            node_id = node_data.get("storage_id")
            node_label = customtkinter.CTkLabel(self.paired_nodes_frame, text=node_name, text_color="white")
            node_label.grid(row=i, column=0, padx=(20, 10), pady=5, sticky="w")
            unpair_button = customtkinter.CTkButton(self.paired_nodes_frame, text="Unpair", command=lambda id=node_id: self._on_unpair_node(id))
            unpair_button.grid(row=i, column=1, padx=(10, 20), pady=5, sticky="e")