import customtkinter as ctk
import requests

class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, switch_to_main):  # Add switch function
        super().__init__(master)
        self.master = master
        self.switch_to_main = switch_to_main # Store the callback
        # ... (Login screen widgets)
        self.login_button = ctk.CTkButton(self, text="Login", command=self.login)
        self.login_button.pack()
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.pack()


    def login(self):
        username = self.username_entry.get()  # Get username from entry
        password = self.password_entry.get()  # Get password
        data = {'username': username, 'password': password}

        try:
            response = requests.post('http://127.0.0.1:5000/api/login', json=data) # Flask server address

            if response.status_code == 200:
                self.switch_to_main(username) # Call the switch function upon successful login
            else:
                error_message = response.json().get('message', 'Login failed') # Extract error message
                self.error_label.configure(text=error_message) # Display error

        except requests.exceptions.RequestException as e:
            self.error_label.configure(text=f"Connection error: {e}")

# ... similar structure for backup_screen.py and restore_screen.py
# You can use requests to interact with the Flask API endpoints.