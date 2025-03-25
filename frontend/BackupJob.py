import customtkinter as gui, requests, tkinter as tk
from PIL import Image
from frontend.components.RemoteExplorer import RemoteExplorer

class BackupJob(gui.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.create_widgets()
        self.backup_demand =  float('inf')
        self.directory_listing = {}
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

        # Row 1: Backup Description, Endpoint, Backup Type
        description_label = gui.CTkLabel(self.form_frame, text="Backup Description")
        description_label.grid(row=0, column=0, padx=(20, 5), pady=(20, 5), sticky="w")

        self.description_entry = gui.CTkEntry(self.form_frame, fg_color="#FFFFFF", border_color="#FFFFFF", text_color="#000000")
        self.description_entry.grid(row=1, column=0, padx=(20, 5), pady=(5, 5), sticky="ew")

        endpoint_label = gui.CTkLabel(self.form_frame, text="Select Endpoint")
        endpoint_label.grid(row=0, column=1, padx=(5, 5), pady=(20, 5), sticky="w")

        endpoints = self.fetch_endpoints("endpoints")
        endpoints.insert(0, "-Select an Option-")
        endpoint_options = endpoints
        self.endpoint_dropdown = gui.CTkComboBox(self.form_frame, values=endpoint_options, dropdown_fg_color="#FFFFFF", dropdown_text_color="#000000", fg_color="#FFFFFF", border_color="#FFFFFF", text_color="#000000")
        self.endpoint_dropdown.grid(row=1, column=1, padx=(5, 5), pady=(5, 5), sticky="ew")

        backup_type_label = gui.CTkLabel(self.form_frame, text="Select Backup Type")
        backup_type_label.grid(row=0, column=2, padx=(5, 20), pady=(20, 5), sticky="w")

        backup_type_options = ["-Select an Option-","Volume", "Directory", "Virtual Machine", "Application"]
        self.backup_type_dropdown = gui.CTkComboBox(self.form_frame, command=lambda label: self.set_responsive_button(label=f"{self.backup_type_dropdown.get()}"), values=backup_type_options,  dropdown_fg_color="#FFFFFF", dropdown_text_color="#000000", fg_color="#FFFFFF", border_color="#FFFFFF", text_color="#000000")
        self.backup_type_dropdown.grid(row=1, column=2, padx=(5, 20), pady=(5, 5), sticky="ew")
        
        self.browse_items_button = gui.CTkButton(self.form_frame, state=tk.DISABLED, text="Browse Backup Items", fg_color="#2b2b2b", command=self.browse_object)
        self.browse_items_button.grid(row=2, column=0, columnspan=3, pady=(10, 5), padx=20, sticky="ew")

        # Row 3: Storage Node, Browse Destination
        storage_node_label = gui.CTkLabel(self.form_frame, text="Primary Storage Node")
        storage_node_label.grid(row=3, column=0, padx=(20, 5), pady=(5, 5), sticky="w")

        storage_node_options = ["Node A", "Node B", "Node C"]
        self.storage_node_dropdown = gui.CTkComboBox(self.form_frame, values=storage_node_options, fg_color="#2b2b2b", border_color="#2b2b2b", text_color="#000000",state=tk.DISABLED)
        self.storage_node_dropdown.grid(row=4, column=0, padx=(20, 5), pady=(5, 5), sticky="ew")

        self.browse_destination_button = gui.CTkButton(self.form_frame, text="Select Storage Destination", state=tk.DISABLED, fg_color="#2b2b2b", command=self.select_storage_node)
        self.browse_destination_button.grid(row=4, column=1, padx=(5, 20), pady=(5, 5), sticky="ew", columnspan=2)

        # Row 5: Make Copies On Another Storage Node Switch + Add another storage button.
        self.copy_switch_var = tk.BooleanVar()
        self.copy_switch = gui.CTkSwitch(self.form_frame, text="Make Copies On Other Storage Nodes", variable=self.copy_switch_var)
        self.copy_switch.grid(row=5, column=0, pady=(20, 5), padx=20, sticky="ew", columnspan=2)

        self.add_storage_button = gui.CTkButton(self.form_frame, text="Add Another Storage", fg_color="#2b2b2b", state=tk.DISABLED)
        self.add_storage_button.grid(row=5, column=2, pady=(20, 5), padx=20, sticky="ew")

        # Row 6: Scrollable Frame for Additional Storage Nodes
        self.additional_storage_frame = gui.CTkScrollableFrame(self.form_frame, fg_color="#2b2b2b")
        self.additional_storage_frame.configure(height=100)
        self.additional_storage_frame._scrollbar.configure(height=10)
        self.additional_storage_frame.grid(row=6, column=0, columnspan=3, pady=(0,0), padx=20, sticky="ew")
        self.additional_storage_frame.grid_columnconfigure(0, weight=1)
        self.additional_storage_frame.grid_columnconfigure(1, weight=1)
        

        # Row within Scrollable Frame: Storage Node Dropdown and Choose Location Button
        self.additional_storage_node_dropdown = gui.CTkComboBox(self.additional_storage_frame, values=storage_node_options, fg_color="#000000", border_color="#000000", text_color="#000000", state=tk.DISABLED)
        self.additional_storage_node_dropdown.grid(row=0, column=0, padx=(5, 5), pady=(5, 5), sticky="ew")

        self.choose_location_button = gui.CTkButton(self.additional_storage_frame, text="Choose Location", state=tk.DISABLED, fg_color="#000000")
        self.choose_location_button.grid(row=0, column=1, padx=(5, 5), pady=(5, 5), sticky="ew")

        # Row 7: Backup Now, Schedule Backup
        self.backup_now_button = gui.CTkButton(self.form_frame, text="Backup Now", state=tk.DISABLED, fg_color="#2b2b2b")
        self.backup_now_button.grid(row=7, column=0, padx=(20, 5), pady=(20,5), sticky="ew")

        self.schedule_backup_button = gui.CTkButton(self.form_frame, text="Schedule Backup", state=tk.DISABLED, fg_color="#2b2b2b")
        self.schedule_backup_button.grid(row=7, column=1, padx=(5, 20), pady=(20, 5), sticky="ew", columnspan=2)

        # Adjusted column configurations
        self.form_frame.columnconfigure(0, weight=1)
        self.form_frame.columnconfigure(1, weight=1)
        self.form_frame.columnconfigure(2, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(1, weight=1)

    def fetch_endpoints(self, obj_type):
        resource_url= f"http://127.0.0.1:8080/zeroapi/v1/objects/{obj_type}"
        auth_token = self.master.retrieve_auth_token()
        zeroheaders = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        del auth_token
        try:
            response = requests.get( resource_url, stream=True, headers=zeroheaders)
            response.raise_for_status()
            endpoint_names = response.json()
            return endpoint_names["names"]
        except requests.exceptions.RequestException as e:
            tk.messagebox.showerror("Fetch Error", f"Failed to fetch {obj_type}: {e}")
            return -1
        except Exception as e:
            tk.messagebox.showerror("Fetch Error", f"An Application Error Occurred, report this to ZeroDown.")
            return -1
    
    def set_responsive_button(self, label):
        if not label.startswith("-"):
            self.browse_items_button.configure(text=f"Browse {label}", state="normal", fg_color="#1F6AA5") 
        else: 
            self.browse_items_button.configure(text="Browse", state="disabled", fg_color="#2b2b2b")

    def get_listing(self, endpoint_name):
        resource_url= f"http://127.0.0.1:8080/zeroapi/v1/listing/{endpoint_name.lower()}"
        zauth_token = self.master.retrieve_auth_token()
        zeroheaders = {"Authorization": f"Bearer {zauth_token}", "Content-Type": "application/json"}
        del zauth_token
        try:
            response = requests.get( resource_url, stream=True, headers=zeroheaders)
            response.raise_for_status()
            directory_listing = response.json()
            self.directory_listing= directory_listing
        except requests.exceptions.RequestException as e:
            tk.messagebox.showerror("Fetch Error", f"Failed to fetch {e}")
            #return -1
        except Exception as e:
            print("ERROR IS",e)
            tk.messagebox.showerror("Fetch Error", f"An Application Error Occurred, report this to ZeroDown.")
            #return -1
    
    def select_storage_node(self):
        print(self.directory_listing)

    def browse_object(self):
        endpoint_name=self.endpoint_dropdown.get()
        title = f'{self.browse_items_button.cget("text")} on {endpoint_name}'
        self.get_listing(endpoint_name)
        RemoteExplorer(self, title, endpoint_name)

        
