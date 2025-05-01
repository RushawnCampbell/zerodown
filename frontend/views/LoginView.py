import customtkinter as gui
import tkinter as tkint
import requests, sys

class Loginview(gui.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.master = master

        self.grid(row=0, column=0, padx=0, pady=0, sticky='nsew')

        self.username_label = gui.CTkLabel(self, text="Username:")
        self.username_label.pack(pady=(5, 0), padx=(0,130))
        self.username_entry = gui.CTkEntry(self, width=200, text_color="#000000", border_width=0)
        self.username_entry.pack(pady=(0, 5))
        self.username_entry.configure(fg_color="#FFFFFF", bg_color="#FFFFFF")

        self.password_label = gui.CTkLabel(self, text="Password:")
        self.password_label.pack(pady=(0, 0), padx=(0,130))
        self.password_entry = gui.CTkEntry(self, show="*", width=200, text_color="#000000", border_width=0)
        self.password_entry.pack(pady=(0, 20))
        self.password_entry.configure(fg_color="#FFFFFF", bg_color="#FFFFFF")

        self.login_button = gui.CTkButton(self, text="Login", command=self.login)
        self.login_button.pack()

    def login(self):
        try: 
            username = self.username_entry.get()
            password = self.password_entry.get()

            response = requests.post("http://127.0.0.1:8080/zeroapi/v1/login", json={"username": username, "password": password})
            statcode = response.status_code
            errorcode = response.raise_for_status()  
            data = response.json()
            zauth_token = data["zauth_token"]
            self.master.store_auth_token(zauth_token=zauth_token)
         
            if statcode == 200:
                self.master.route_home()
                self.master.tool_bar.grid(row=1, column=0, padx=0, pady=0, sticky="ew")
                self.master.tool_bar.configure(height=35) 
                self.destroy() 
    
            else:
                tkint.messagebox.showerror("Something Went Wrong", "Check your username and password then try again.")

        except requests.exceptions.RequestException as e:
            tkint.messagebox.showerror("Something Went Wrong", "Check your username and password then try again.")

        except Exception as e:
            tkint.messagebox.showerror("Render Error", "An Error Occurred While Rendering This View. Please Report To ZeroDown Support If It Reoccurrs.")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            line_number = exc_traceback.tb_lineno
            print(f"An exception occurred: {e}")
            print(f"Line number: {line_number}")
