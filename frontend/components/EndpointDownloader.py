import customtkinter as gui
import tkinter as tk
import os, requests
from frontend.components.Popup import Popup

class EndpointDownloader(Popup):
    def __init__(self, master, title):
        super().__init__(master, title)
        self.configure_body()
        self.get_endpoint_setup("zeroendpoint_setup")


    def configure_body(self):

        self.configure(fg_color="#FFFFFF")
        self.protocol("WM_DELETE_WINDOW", self.disable_close)
        
        self.columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0) 

        gif_label = gui.CTkLabel(self, text="")
        gif_label.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        instruct1 = gui.CTkLabel(self, text="1. Run the downloaded zeroendpoint_setup.exe as Administrator on the Endpoint(device you would like to backup).",
                                        wraplength=390,
                                        )
        instruct1.grid(row=1, column=0, sticky="w", padx=(20, 20), pady=10) 
        instruct1.configure(text_color="black") 

        instruct2 = gui.CTkLabel(self, text="2. Close this window and test the connection to the newly added Endpoint",
                                        wraplength=390,
                                        )
        instruct2.grid(row=2, column=0, sticky="w", padx=(20, 20), pady=10) 
        instruct2.configure(text_color="black") 
        #fg_color="#1fa59d"
        close_button = gui.CTkButton(self, text="Close(Downloading...)", command=self.on_close)
        close_button.configure(state="disabled", fg_color="#2b2b2b")
        close_button.grid(row=3, column=0, pady=20) 

        gif_path = os.path.join("frontend", "assets", "images", "download.gif")
        self.display_gif(gif_label, gif_path, 100, 100)
    
    def get_endpoint_setup(self, filename):
        resource_url= f"http://127.0.0.1:8080/zeroapi/v1/download/{filename}"
        auth_token = self.master.master.retrieve_auth_token()
        zeroheaders = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        del auth_token
        try:
            response = requests.get( resource_url, stream=True, headers=zeroheaders)
            response.raise_for_status()
            

            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            print("DPATH", downloads_path)
            file_path = os.path.join(downloads_path, f"{filename}.exe")
            print("FPATH", file_path)

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  
                        f.write(chunk)

            print(f"File downloaded successfully to: {file_path}")
            
            tk.messagebox.showinfo("Download Complete", f"File '{filename}' downloaded successfully!")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading file: {e}")
            tk.messagebox.showerror("Download Error", f"An error occurred during download: {e}")
        except Exception as e:
            print(f"An unexpected error occured: {e}")
            tk.messagebox.showerror("Unexpected Error", f"An unexpected error occured: {e}")
