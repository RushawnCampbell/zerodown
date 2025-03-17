import customtkinter as gui
import tkinter as tk
import os, requests
from frontend.components.Popup import Popup
from PIL import Image

class TestConnection(Popup):
    def __init__(self, master, title, ip, authorized_user):
        super().__init__(master, title)
        self.master = master
        self.ip = ip
        self.authorized_user = authorized_user
        self.status_label= None
        self.configure_body()
        self.test_object_connection()

    def configure_body(self):
        self.configure(fg_color="#FFFFFF")
        self.protocol("WM_DELETE_WINDOW", self.disable_close)

        self.rowconfigure(0, weight=1) 

        main_frame = gui.CTkFrame(self, fg_color="transparent") 
        main_frame.pack(expand=True) 

        gif_label = gui.CTkLabel(main_frame, text="")
        gif_label.pack(pady=(0, 5)) 

        self.status_label = gui.CTkLabel(main_frame, text= f"Attempting Secure {self.master.reg_type} Connection...")
        self.status_label.pack(pady=(5, 0)) 
        self.status_label.configure(text_color="black")

        gif_path = os.path.join("frontend", "assets", "images", "testing.gif")
        self.display_gif(gif_label, gif_path, 100, 100)

    def test_object_connection(self):
        resource_url = "http://127.0.0.1:8080/zeroapi/v1/test_connection"
        auth_token = self.master.master.retrieve_auth_token()
        zeroheaders = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        del auth_token

        try:
            response = requests.post(resource_url, headers=zeroheaders, json={"hostname": self.master.ip_value.get(), "authorized_user": self.master.user_value.get(), "reg_type":self.master.reg_type.replace(" ", "").lower()})
            response.raise_for_status()
            data = response.json()
            fetched_pub = data["response"]

            if response.status_code == 200:
                self.master.fetched_pub = fetched_pub
                self.master.connection_successful = True
                self.master.completed_image = Image.open("./frontend/assets/icons/check.png")
                self.master.ctk_completed_image=gui.CTkImage(light_image=self.master.completed_image, dark_image=self.master.completed_image, size=(25, 25))
                self.master.step3_button.configure(image=self.master.ctk_completed_image, fg_color="#1fa59d", text="Connection Successful")
                self.status_label.configure(text_color="#1fa59d", text="Connection Successful")
                #self.master.step4_button.custom_data["test_result"] = 1
                self.master.step4_button.configure(state="normal", fg_color="#1F6AA5")
                self.after(2000, self.on_close)
            else:
                tk.messagebox.showerror("Connection Failed", f"{self.master.reg_type} connection failed.")
                self.status_label.configure(text_color="#cc3300", text="Something didn't go as planned. Contact ZeroDown Support for assistance.")
                self.master.warning_image = Image.open("./frontend/assets/icons/danger.png")
                self.master.ctk_warning_image = gui.CTkImage(light_image=self.master.warning_image, dark_image=self.master.warning_image, size=(25, 25))
                self.master.step3_button.configure(fg_color="#cc3300", text="Connection Failed: Retry Test", image=self.master.ctk_warning_image )
                #self.master.step4_button.custom_data["test_result"] = 0
                self.master.step4_button.configure(state="disabled", fg_color="#2b2b2b")
                self.after(5000, self.on_close)

        except requests.exceptions.RequestException as e:
            tk.messagebox.showerror("Connection Error", f"An error occurred during connection.")
            self.status_label.configure(text_color="#cc3300", text=f"Connection failed, Check your {self.master.reg_type} setup and information ")
            self.master.warning_image = Image.open("./frontend/assets/icons/danger.png")
            self.master.ctk_warning_image = gui.CTkImage(light_image=self.master.warning_image, dark_image=self.master.warning_image, size=(25, 25))
            self.master.step3_button.configure(fg_color="#cc3300", text="Connection Failed: Retry Test", image=self.master.ctk_warning_image )
            #self.master.step4_button.custom_data["test_result"] = 0
            self.master.step4_button.configure(state="disabled", fg_color="#2b2b2b")
            self.after(5000, self.on_close)
        except Exception as e:
            tk.messagebox.showerror("Unexpected Error", f"An unexpected error occurred")
            self.status_label.configure(text_color="#cc3300", text="Connection failed, An unexpected error occurred. Contact ZeroDown Support for further assistance.")
            self.master.warning_image = Image.open("./frontend/assets/icons/danger.png")
            self.master.ctk_warning_image = gui.CTkImage(light_image=self.master.warning_image, dark_image=self.master.warning_image, size=(25, 25))
            self.master.step3_button.configure(fg_color="#cc3300", text="Connection Failed: Retry Test", image=self.master.ctk_warning_image )
            self.master.step4_button.custom_data["test_result"] = 0
            self.master.step4_button.configure(state="disabled", fg_color="#2b2b2b")
            self.after(5000, self.on_close)