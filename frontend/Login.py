import customtkinter as gui

class Login(gui.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        #self.switch_to_backup_view = switch_to_backup_view

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

        print("User:", username,"has logged in")

        """try:
            response = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            data = response.json()

            if data.get("success"): #check if there's a success key
                messagebox.showinfo("Success", "Login successful!")
                self.switch_to_backup_view(data.get("user_id")) # Pass user_id to the next view
                self.pack_forget() # Hide this view
            else:
                messagebox.showerror("Error", data.get("message", "Invalid username or password."))

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"API request failed: {e}")
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Invalid JSON response from API: {e}")"""