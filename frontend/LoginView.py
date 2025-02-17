import customtkinter as gui
import requests, json

class LoginView(gui.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        #self.switch_to_backup_view = switch_to_backup_view

        self.master = master

        self.grid(row=0, column=0, padx=0, pady=0, sticky='nsew')

        self.username_label = gui.CTkLabel(self, text="Username:")
        self.username_label.pack(pady=(5, 0), padx=(0,130))
        self.username_entry = gui.CTkEntry(self, width=200)
        self.username_entry.pack(pady=(0, 5))

        self.password_label = gui.CTkLabel(self, text="Password:")
        self.password_label.pack(pady=(0, 0), padx=(0,130))
        self.password_entry = gui.CTkEntry(self, show="*", width=200)
        self.password_entry.pack(pady=(0, 20))

        self.login_button = gui.CTkButton(self, text="Login", command=self.login)
        self.login_button.pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            response = requests.post("http://127.0.0.1:8080/zeroapi/v1/login", json={"username": username, "password": password})
            statcode = response.status_code
            errorcode = response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            data = response.json()
            #print("STATUS IS", type(statcode))
            #print("ERROR IS", errorcode)
            #print("DATA IS", data)
            if statcode == 200:
                print("Successful login")
                self.master.show_home_view() 
                self.pack_forget() # Hide this view
                self.master.tool_bar.grid(row=1, column=0, padx=0, pady=0, sticky="ew")
                self.master.tool_bar.configure(height=35)
            else:
                print("Invalid username or password")

        except requests.exceptions.RequestException as e:
            print("API request failed")
            print("ERROR IS ", e)
        except json.JSONDecodeError as e:
            print("INVALID JSON")
            print("ERROR IS ", e)