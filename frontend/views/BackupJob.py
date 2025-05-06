import customtkinter as gui, traceback, json, requests, tkinter as tk
from PIL import Image
from frontend.components.RemoteExplorer import RemoteExplorer
from frontend.components.JobStatus import JobStatus
from frontend.components.ScheduleJob import ScheduleJob
from frontend.Utility.CommonMethods import CommonMethods

class Backupjob(gui.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("ZeroDown: Create Backup Job")
        self.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.endpoint_name = None
        self.storage_node_dropdown = None
        self.selected_storage = None
        self.backup_job_name =None
        self.create_widgets()
        self.backup_demand =  0.00
        self.available_storage_size = 0.00
        self.volumes_with_size = {}
        self.volumes = []
        self.selected_endpoint_info = {}
        self.selected_storage_info = {}
        self.sch_datetime = None
        self.sch_frequency = None
        self.sch_day =  None
        self.virtual_machines = ["VM 1", "VM 2", "VM 3", "VM 4"]
        self.applications = ['APP ONE', 'APP TWO', 'APP THREE', 'APP FOUR']

    def create_widgets(self):
        # Title Frame
        self.title_frame = gui.CTkFrame(self)
        self.title_frame.grid(row=0, column=0, columnspan=3, sticky="ew")

        title_label = gui.CTkLabel(self.title_frame, text="Create Backup Job", font=gui.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(10, 20))

        # Form Body Frame
        self.form_frame = gui.CTkFrame(self, fg_color="#000000")
        self.form_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=40, pady=20)

        # Row 1: Backup Description, Endpoint
        backup_job_label = gui.CTkLabel(self.form_frame, text="Backup Job Name")
        backup_job_label.grid(row=0, column=0, padx=(20, 5), pady=(20, 5), sticky="w")

        self.backup_job_name = gui.CTkEntry(self.form_frame, fg_color="#FFFFFF", border_color="#FFFFFF", text_color="#000000")
        self.backup_job_name.bind("<FocusOut>", lambda event: self.master_validator(widget_label="job_name", event=event))
        self.backup_job_name.grid(row=1, column=0, padx=(20, 5), pady=(5, 5), sticky="ew")

        endpoint_label = gui.CTkLabel(self.form_frame, text="Select Endpoint")
        endpoint_label.grid(row=0, column=1, padx=(5, 20), pady=(20, 5), sticky="w")

        endpoints = self.fetch_objects("endpoint_names")
        endpoints.insert(0, "-Select an Option-")
    
        self.endpoint_dropdown = gui.CTkComboBox(self.form_frame, values=endpoints, dropdown_fg_color="#FFFFFF", dropdown_text_color="#000000", fg_color="#FFFFFF", border_color="#FFFFFF", text_color="#000000", command=lambda selected_endpoint: self.activate_browse_button(selected_endpoint))
        self.endpoint_dropdown.grid(row=1, column=1, padx=(5, 20), pady=(5, 5), sticky="ew")
        
        self.browse_items_button = gui.CTkButton(self.form_frame, state=tk.DISABLED, text="Select an Endpoint To Browse", fg_color="#2b2b2b", command=self.browse_object)
        self.browse_items_button.grid(row=2, column=0, columnspan=2, pady=(10, 5), padx=20, sticky="ew")

        # Row 3: Storage Node, Browse Destination
        storage_node_label = gui.CTkLabel(self.form_frame, text="Primary Storage Node")
        storage_node_label.grid(row=3, column=0, padx=(20, 5), pady=(5, 5), sticky="w")

        storagenodes = self.fetch_objects("storage_names")
        storagenodes.insert(0, "-Select an Option-")

        self.storage_node_dropdown = gui.CTkComboBox(self.form_frame, values=storagenodes, fg_color="#2b2b2b", border_color="#2b2b2b", text_color="#000000", state=tk.DISABLED, command= lambda selected_storage: self.activate_select_destination(selected_storage))
        self.storage_node_dropdown.bind("<FocusOut>", lambda event: self.master_validator(widget_label="storage_node_val", event=event))
        self.storage_node_dropdown.grid(row=4, column=0, padx=(20, 5), pady=(5, 5), sticky="ew")

        self.browse_destination_button = gui.CTkButton(self.form_frame, text="Select Backup Destination", state=tk.DISABLED, fg_color="#2b2b2b", command= self.select_storage_destination)
        self.browse_destination_button.grid(row=4, column=1, padx=(5, 20), pady=(5, 5), sticky="ew")
        

        # Row 5: Make Copies On Another Storage Node Switch + Add another storage button.
        self.copy_switch_var = tk.BooleanVar()
        self.copy_switch = gui.CTkSwitch(self.form_frame, text="Make Copies On Other Storage Nodes", variable=self.copy_switch_var)
        self.copy_switch.grid(row=5, column=0, pady=(20, 5), padx=20, sticky="ew", columnspan=2)

        self.add_storage_button = gui.CTkButton(self.form_frame, text="Add Another Storage", fg_color="#2b2b2b", state=tk.DISABLED)
        self.add_storage_button.grid(row=5, column=1, pady=(20, 5), padx=20, sticky="ew")

        # Row 6: Scrollable Frame for Additional Storage Nodes
        self.additional_storage_frame = gui.CTkScrollableFrame(self.form_frame, fg_color="#2b2b2b")
        self.additional_storage_frame.configure(height=100)
        self.additional_storage_frame._scrollbar.configure(height=10)
        self.additional_storage_frame.grid(row=6, column=0, columnspan=2, pady=(0,0), padx=20, sticky="ew")
        self.additional_storage_frame.grid_columnconfigure(0, weight=1)
        self.additional_storage_frame.grid_columnconfigure(1, weight=1)
        

        # Row within Scrollable Frame: Storage Node Dropdown and Choose Location Button
        self.additional_storage_node_dropdown = gui.CTkComboBox(self.additional_storage_frame, values=storagenodes, fg_color="#000000", border_color="#000000", text_color="#000000", state=tk.DISABLED)
        self.additional_storage_node_dropdown.grid(row=0, column=0, padx=(5, 5), pady=(5, 5), sticky="ew")

        self.choose_location_button = gui.CTkButton(self.additional_storage_frame, text="Choose Location", state=tk.DISABLED, fg_color="#000000")
        self.choose_location_button.grid(row=0, column=1, padx=(5, 5), pady=(5, 5), sticky="ew")

        # Row 7: Backup Now, Schedule Backup
        self.backup_now_button = gui.CTkButton(self.form_frame, text="Backup Now", state=tk.DISABLED, fg_color="#2b2b2b", command=self.backup_now)
        self.backup_now_button.grid(row=7, column=0, padx=(20, 5), pady=(20,5), sticky="ew")

        self.schedule_backup_button = gui.CTkButton(self.form_frame, text="Schedule Backup", state=tk.DISABLED, fg_color="#2b2b2b", command=self.schedule_job)
        self.schedule_backup_button.grid(row=7, column=1, padx=(5, 20), pady=(20, 5), sticky="ew")

        # Adjusted column configurations
        self.form_frame.columnconfigure(0, weight=1)
        self.form_frame.columnconfigure(1, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(1, weight=1)

    def fetch_objects(self, obj_type):
        try:
            objects = CommonMethods.get_objects(obj_type, self.master.app_name, self.master.windows_user)
            if objects == None:
               tk.messagebox.showerror("Failed to Get Items", f"Failed to get requested items")
               return objects
            else:
                return objects
        except Exception as e:
            tk.messagebox.showerror("Fetch Error", f"An Application Error Occurred, report this to ZeroDown.")
            return None


    def get_endpoint_volumes(self, endpoint_name):
        resource_url= f"http://127.0.0.1:8080/zeroapi/v1/endpoint/listing/{endpoint_name.lower()}"
        zauth_token = self.master.retrieve_auth_token()
        zeroheaders = {"Authorization": f"Bearer {zauth_token}", "Content-Type": "application/json"}
        del zauth_token
        try:
            response = requests.get( resource_url, stream=True, headers=zeroheaders)
            response.raise_for_status()
            self.volumes_with_size = json.loads(response.json())
            for obj in self.volumes_with_size:
                self.volumes.append(obj)
        except requests.exceptions.RequestException as e:
            tk.messagebox.showerror("Fetch Error", f"Failed to fetch {e}")
            #return -1
        except Exception as e:
            print("ERROR IS",e)
            tb = traceback.extract_tb(e.__traceback__)
            last_frame = tb[-1]
            if tb:
                lineno = last_frame.lineno
                print("LINE NUM IS", lineno)
            tk.messagebox.showerror("Fetch Error", f"An Application Error Occurred, report this to ZeroDown.")
            #return -1

    def get_storage_volumes(self, storage_name):
        resource_url= f"http://127.0.0.1:8080/zeroapi/v1/storage/volumes/{storage_name.lower()}"
        zauth_token = self.master.retrieve_auth_token()
        zeroheaders = {"Authorization": f"Bearer {zauth_token}", "Content-Type": "application/json"}
        del zauth_token
        try:
            response = requests.get( resource_url, stream=True, headers=zeroheaders)
            response.raise_for_status()
            self.volumes_with_size = json.loads(response.json())
            for obj in self.volumes_with_size:
                self.volumes.append(obj)
        except requests.exceptions.RequestException as e:
            tk.messagebox.showerror("Fetch Error", f"Failed to fetch {e}")
            #return -1
        except Exception as e:
            print("ERROR IS",e)
            tb = traceback.extract_tb(e.__traceback__)
            last_frame = tb[-1]
            if tb:
                lineno = last_frame.lineno
                print("LINE NUM IS", lineno)
            tk.messagebox.showerror("Fetch Error", f"An Application Error Occurred, report this to ZeroDown.")
            #return -1

    def activate_browse_button(self, selected_endpoint):
        if selected_endpoint !="" and selected_endpoint != "-Select an Option-":
            self.browse_items_button.configure(state=tk.NORMAL, fg_color="#1F6AA5", text=f"Browse {selected_endpoint} Backup Items")
        else:
            self.browse_items_button.configure(state=tk.DISABLED, fg_color="#2b2b2b", text="Select an Endpoint To Browse")
    
    def activate_select_destination(self, selected_storage):
        storage_node_val =  self.master_validator(widget_label="storage_node_val")
        if storage_node_val < 1:
            return -1
        self.selected_storage= selected_storage
        self.get_storage_volumes(selected_storage)
        self.browse_destination_button.configure(state="normal", fg_color="#1F6AA5")


    def browse_object(self):
        self.backup_demand = 0.00
        self.endpoint_name=self.endpoint_dropdown.get()
        title = f'{self.browse_items_button.cget("text")}'
        self.get_endpoint_volumes(self.endpoint_name)
        RemoteExplorer(self, title, self.endpoint_name, "endpoint", "backup")

    def select_storage_destination(self):
        title = f' Storage Nodes on {self.selected_storage}'
        RemoteExplorer(self, title, self.selected_storage, "storage", "backup")


    def backup_now(self):
        job_name_vf = self.master_validator(widget_label="job_name") #job name validation factor
        storage_node_vf = self.master_validator(widget_label="storage_node_val") #storage node validation factor
        endpoint_vf = self.master_validator(widget_label="endpoint_val") #endpoint  validation factor

        if  job_name_vf <= 0:
            tk.messagebox.showerror("Invalid Job Name", "You must enter a valid Job Name")

        if storage_node_vf <= 0:
            tk.messagebox.showerror("Invalid Storage Node Selection", "You Must Select A Storage Node")
        
        if endpoint_vf <= 0:
             tk.messagebox.showerror("Invalid Endpoint Selection", "You Must Select An Endpoint")

        if  not job_name_vf <= 0 and not storage_node_vf <= 0 and not endpoint_vf <= 0:
            resource_url= f"http://127.0.0.1:8080/zeroapi/v1/backup/first_time"
            zauth_token = self.master.retrieve_auth_token()
            zeroheaders = {"Authorization": f"Bearer {zauth_token}", "Content-Type": "application/json"}
            try:
                response = requests.post( resource_url, stream=True, headers=zeroheaders, json={"endpoint_name" : self.endpoint_name, "backup_targets": self.selected_endpoint_info, "backup_destinations": self.selected_storage_info, "name": self.backup_job_name.get()})
                response.raise_for_status()
                response= response.json()
                in_progress_num = response['in_progress']
                job_id = response['job_id']

                if  in_progress_num >= 1:
                    title = f"Backup Job: {self.backup_job_name.get()} In Progress"
                    JobStatus(self, title, in_progress_num, job_id )
                else:
                    tk.messagebox.showerror("Backup Error", f"Something Went Wrong: Failed to start backup")

            except requests.exceptions.RequestException as e:
                tk.messagebox.showerror("Backup Error", f"An unexpected error occurred. Please try again or contact ZeroDown Support for help.")


    def master_validator(self, widget_label, event=None):
        if widget_label == "job_name":
            if  self.backup_job_name.get() == None or self.backup_job_name.get() == ""  or self.backup_job_name.get() == "Name this Backup Job":
                self.backup_job_name.configure(text_color="#cc3300")
                self.backup_job_name.delete(0, "end")
                self.backup_job_name.insert(0,f"Name this Backup Job")
                return 0
            else:
                self.backup_job_name.configure(text_color="#000000")
                return 1
        
        if widget_label == "endpoint_val":
            if  self.endpoint_dropdown.get() == "-Select an Option-":
                self.browse_items_button.configure(state="disabled")
                return 0
            else:
                self.browse_items_button.configure(state="normal")
                return 1
            

        if widget_label == "storage_node_val":
            if  self.storage_node_dropdown.get() == "-Select an Option-":
                self.browse_destination_button.configure(state="disabled")
                return 0
            else:
                self.browse_destination_button.configure(state="normal")
                return 1

        return -1
    
    def schedule_job(self):
        job_name_vf = self.master_validator(widget_label="job_name") #job name validation factor
        storage_node_vf = self.master_validator(widget_label="storage_node_val") #storage node validation factor
        endpoint_vf = self.master_validator(widget_label="endpoint_val") #endpoint  validation factor

        if  job_name_vf <= 0:
            tk.messagebox.showerror("Invalid Job Name", "You must enter a valid Job Name")

        if storage_node_vf <= 0:
            tk.messagebox.showerror("Invalid Storage Node Selection", "You Must Select A Storage Node")
        
        if endpoint_vf <= 0:
             tk.messagebox.showerror("Invalid Endpoint Selection", "You Must Select An Endpoint")

        if  not job_name_vf <= 0 and not storage_node_vf <= 0 and not endpoint_vf <= 0:
            ScheduleJob(self, "Scheduling Job", job_name=self.backup_job_name.get() )
    