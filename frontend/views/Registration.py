import customtkinter as gui, ipaddress, requests, tkinter as tk
from frontend.components.SetupDownloader import SetupDownloader
from frontend.components.TestConnection import TestConnection
from PIL import Image


class Registration(gui.CTkFrame):
    def __init__(self, master, reg_type):
        super().__init__(master)
        self.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.reg_type = reg_type
        self.master = master
        self.fetched_pub = None
        self.step2_button = None
        self.step3_button = None
        self.step4_button = None 
        self.ip_value= None
        self.user_value= None
        self.ctk_completed_image = None
        self.ctk_warning_image = None
        self.warning_image= None
        self.completed_image = None
        self._configure_ui()
        self._create_widgets()
        self._layout_widgets()

    def _configure_ui(self):
        """Configures the UI appearance and grid layout."""
        self.configure(fg_color="#2B2B2B")
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _create_widgets(self):
        """Creates and initializes all UI widgets."""
        self.view_title_frame = gui.CTkFrame(self)
        self.view_title = gui.CTkLabel(
            self.view_title_frame,
            text= f"Register {self.reg_type}",
            font=gui.CTkFont(size=20, weight="bold"),
            wraplength=700,
            justify="center",
        )

        self.form_body = gui.CTkFrame(self)
        self.form_body.configure(fg_color="#000000")
        self.form_body.grid_columnconfigure(0, weight=1)
        for i in range(5): #added one more row
            self.form_body.grid_rowconfigure(i * 2, weight=1)
            self.form_body.grid_rowconfigure(i * 2 + 1, weight=1)

        self.step1_label = gui.CTkLabel(self.form_body, text=f"STEP 1: Define {self.reg_type}", font=gui.CTkFont(size=15, weight="bold"), anchor="w")
        self.step1_entry_frame = gui.CTkFrame(self.form_body)
        self.step1_entry_frame.grid_columnconfigure(0, weight=1)
        self.step1_entry_frame.grid_columnconfigure(1, weight=1)
        self.step1_entry_frame.grid_columnconfigure(2, weight=1)
        self.step1_entry_frame.configure(fg_color="#000000")

        self.object_name_label= gui.CTkLabel(self.step1_entry_frame, text="Name", anchor="center")
        self.object_name = gui.CTkEntry(self.step1_entry_frame, text_color="#000000", border_color="#FFFFFF")
        self.object_name.bind("<FocusOut>", lambda event: self.master_validator(widget_label="name",event=event))
        self.object_name.configure(fg_color="#FFFFFF")

        self.ip_label = gui.CTkLabel(self.step1_entry_frame, text="IP Address", anchor="center")
        self.ip_value = gui.CTkEntry(self.step1_entry_frame, text_color="#000000", border_color="#FFFFFF")
        self.ip_value.bind("<FocusOut>", lambda event: self.master_validator(widget_label="ip", event=event))
        self.ip_value.configure(fg_color="#FFFFFF")

        self.user_label = gui.CTkLabel(self.step1_entry_frame, text= f"Authorized User", anchor="center")
        self.user_value = gui.CTkEntry(self.step1_entry_frame, text_color="#000000", border_color="#FFFFFF")
        self.user_value.bind("<FocusOut>", lambda event: self.master_validator(widget_label="user", event=event))
        self.user_value.configure(fg_color="#FFFFFF")

        self.step2_label = gui.CTkLabel(self.form_body, text=f"STEP 2: Download {self.reg_type} Setup File",font=gui.CTkFont(size=15, weight="bold"), anchor="w")
        self.download_image = Image.open("./frontend/assets/icons/download.png")
        self.ctk_download_image = gui.CTkImage(light_image=self.download_image, dark_image=self.download_image, size=(25, 25))
        self.step2_button = gui.CTkButton(self.form_body,image=self.ctk_download_image, text=f"Download {self.reg_type} Setup", command=self.download_setup)

        self.step3_label = gui.CTkLabel(self.form_body, text="STEP 3: Test Connection", font=gui.CTkFont(size=15, weight="bold"), anchor="w")
        self.test_image = Image.open("./frontend/assets/icons/Test.png")
        self.ctk_test_image = gui.CTkImage(light_image=self.test_image, dark_image=self.test_image, size=(25, 25))
        self.step3_button = gui.CTkButton(self.form_body,image=self.ctk_test_image, text="Test Connection (Not Yet Tested)", command=self.test_connection)
        self.step3_button.custom_data = {"test_result": 0}

        self.complete_reg_image = Image.open("./frontend/assets/icons/check-list.png")
        self.ctk_complete_reg_image = gui.CTkImage(light_image=self.complete_reg_image, dark_image=self.complete_reg_image, size=(25, 25))
        self.step4_button = gui.CTkButton(self.form_body, image=self.ctk_complete_reg_image, text="Complete Registration", command=self.register_object)
        self.step4_button.configure(state="disabled", fg_color="#2b2b2b") # #1fa59d

    def _layout_widgets(self):
        """Arranges the widgets within the grid layout."""
        self.view_title_frame.grid(row=0, column=0, padx=40, pady=20, sticky="nsew")
        self.view_title.pack(pady=(0, 0), padx=0, fill="x")

        self.form_body.grid(row=1, column=0, padx=50, pady=(0, 20), sticky="nsew")

        self.step1_label.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.step1_entry_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.object_name_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.object_name.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.ip_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.ip_value.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.user_label.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self.user_value.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

        self.step2_label.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.step2_button.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.step3_label.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.step3_button.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.step4_button.grid(row=7, column=0, padx=20, pady=(0, 10), sticky="ew")

    def download_setup(self):
        download_pup = SetupDownloader(self, f"Download {self.reg_type} Setup")

    def test_connection(self):
        authorized_user = self.user_value.get()
        ip_stat = self.master_validator(widget_label="ip")
        user_stat = self.master_validator(widget_label="user")
        if ip_stat == 0 or user_stat == 0:
            return -1 
        else:
            ip = self.ip_value.get()
            TestConnection(self, f"Testing {self.reg_type} Connection", ip=ip, authorized_user=authorized_user)
            del ip

    def register_object(self):
        name_stat = self.master_validator(widget_label="name")
        ip_stat = self.master_validator(widget_label="ip")
        user_stat = self.master_validator(widget_label="user")
        if ip_stat == 0 or user_stat == 0 or name_stat==0:
            return -1
        else:
            prepped_type= self.reg_type.replace(" ", "").lower()
            resource_url = f"http://127.0.0.1:8080/zeroapi/v1/register/{prepped_type}"
            auth_token = self.master.retrieve_auth_token()
            zeroheaders = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
            del auth_token
            
            self.warning_image = Image.open("./frontend/assets/icons/danger.png")
            self.ctk_warning_image = gui.CTkImage(light_image=self.warning_image, dark_image=self.warning_image, size=(25, 25))
    
            self.completed_image = Image.open("./frontend/assets/icons/check.png")
            self.ctk_completed_image = gui.CTkImage(light_image=self.completed_image, dark_image=self.completed_image, size=(25, 25))
            
            try:
                response=None
                if self.reg_type.replace(" ", "").lower() == "storagenode":
                    response = requests.post(resource_url, headers=zeroheaders, json={"name": self.object_name.get(), "ip": self.ip_value.get(), "authorized_user": self.user_value.get(), "pub_key" : self.fetched_pub})
                if self.reg_type.replace(" ", "").lower() == "endpoint":
                    response = requests.post(resource_url, headers=zeroheaders, json={"name": self.object_name.get(), "ip": self.ip_value.get(), "authorized_user": self.user_value.get()})
                del self.fetched_pub
                response.raise_for_status()
                if response.status_code == 200:
                    self.step4_button.configure(text=f"{self.reg_type} Registered Successfully", fg_color="#1fa59d", image=self.ctk_completed_image)
                else:
                    self.step4_button.configure(fg_color="#cc3300", text="Registration Failed: Try Again Later", image=self.ctk_warning_image )
            except requests.exceptions.RequestException as e:
                tk.messagebox.showerror("Registration Error", f"We encountered an error while registering your {self.reg_type}.")
                self.step4_button.configure(fg_color="#cc3300", text="Registration Failed: Try Again Later", image=self.ctk_warning_image )
    
    def master_validator(self, widget_label, event=None):
        if widget_label == "ip":    
            try:
                ip_entry = self.ip_value.get()
                ipaddress.ip_address(ip_entry)
                self.ip_value.configure(text_color="#000000") 
                return 1 
            except ValueError:
                self.ip_value.configure(text_color="#cc3300")
                self.ip_value.delete(0, "end")
                self.ip_value.insert(0,"Invalid IP ")
                return 0
        
        if widget_label == "name":
            if  self.object_name.get() == None or self.object_name.get() == "":
                self.object_name.configure(text_color="#cc3300")
                self.object_name.delete(0, "end")
                self.object_name.insert(0,f"Name this {self.reg_type}")
                return 0
            else:
                self.object_name.configure(text_color="#000000")
                return 1
        
        if widget_label == "user":
            if  self.user_value.get() == None or self.user_value.get() == "":
                self.user_value.configure(text_color="#cc3300")
                self.user_value.delete(0, "end")
                self.user_value.insert(0,"You must enter a username")
                return 0
            else:
                self.user_value.configure(text_color="#000000")
                return 1
        return -1
        
