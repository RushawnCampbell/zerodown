import customtkinter as gui
import tkinter as tk
import os, requests, platform, time
from PIL import Image,ImageTk

class RestoreJob(gui.CTkToplevel):
    def __init__(self, master, title, job_id):
        super().__init__(master)
        self.master = master
        self.job_id = job_id
        self.status_label= None
        self.is_complete = False  
        
        self.after(300, self.set_icon)
        self.title(title)
        self.set_window_position(430,300)
        self.transient(master)
        self.fade_app()


        self.configure_body()
        #self.monitor_status() 

    def configure_body(self):
        self.configure(fg_color="#FFFFFF")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.rowconfigure(0, weight=1)

        main_frame = gui.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True)

        gif_label = gui.CTkLabel(main_frame, text="")
        gif_label.pack(pady=(0, 5))

        status_text = f"Restoring "
        self.status_label = gui.CTkLabel(main_frame, text=status_text)
        self.status_label.pack(pady=(5, 0))
        self.status_label.configure(text_color="#1fa59d")

        gif_path = os.path.join("frontend", "assets", "icons", "restore.gif")
        self.display_gif(gif_label, gif_path, 100, 100)

        #self.close_button = gui.CTkButton(self, text="Close(Restoration will continue to run)", command=self.on_close)
        #self.close_button.configure(state="normal", fg_color="#1fa59d")
        #self.close_button.pack(pady=20)

    def get_status(self):
        resource_url= f"http://127.0.0.1:8080/zeroapi/v1/restore/get_status"
        zauth_token = self.master.master.retrieve_auth_token()
        zeroheaders = {"Authorization": f"Bearer {zauth_token}", "Content-Type": "application/json"}
        try:
            response = requests.post( resource_url, stream=True, headers=zeroheaders, json={"job_id" : self.job_id})
            response.raise_for_status()
            data = response.json()
            return {"success": data.get("success"), "error" : data.get("error")}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching status: {e}")
            return {"success": [], "error" : []}
        

    def monitor_status(self):
        if not self.is_complete:
            status = self.get_status()
            self.vol_with_success = status['success']
            self.vol_with_error = status['error']
            self.num_success += len(self.vol_with_success) 
            self.num_error += len(self.vol_with_error)
            if self.num_success  + self.num_error == self.total_storage_volumes:
            
                if self.num_success == self.total_storage_volumes and self.num_error == 0:
                    self.status_label.configure(text="All Volumes Backed Up!", text_color="#1fa59d")
                    self.failed_volumes_label.configure(text=f"Failed Volumes: {self.num_error}")
                    success_vol_str = self.vol_report(self.vol_with_success)
                    self.volumes_backed_up_label.configure(text=f"Volumes Backed Up: {success_vol_str}", text_color="#1fa59d")

                elif self.num_success == 0 and self.num_error >= 1 :
                    self.status_label.configure(text="All Volumes Failed To Backup!", text_color="#cc3300")
                    self.volumes_backed_up_label.configure(text=f"Volumes Backed Up: {self.num_success}", text_color="#1fa59d")
                    failed_vol_str = self.vol_report(self.vol_with_error)
                    self.failed_volumes_label.configure(text=f"Failed Volumes: {failed_vol_str}", text_color="#cc3300")

                elif self.num_success >= 1 and self.num_error >= 1:
                    self.status_label.configure(text="Backup Partially Complete!", text_color="#cc6d00")
                    failed_vol_str = self.vol_report( self.vol_with_error)
                    self.failed_volumes_label.configure(text= f"Failed Volumes: {failed_vol_str}", text_color="#cc3300")
                    success_vol_str = self.vol_report(self.vol_with_success)
                    self.volumes_backed_up_label.configure(text=f"Volumes Backed Up: {success_vol_str}", text_color="#1fa59d")  
                self.close_button.configure(text="Close")
                
            else:
                self.after(15000, self.monitor_status)

    def set_window_position(self, window_width, window_height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2  
        y = (screen_height - window_height) // 2  

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.resizable(width=False, height=False)

    def set_window_position_top_centered(self, window_width, window_height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = 0  

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.resizable(width=False, height=False)

    def set_icon(self):
        try:
            icon_path_png = os.path.join("frontend", "assets", "icons", "zerodown.png")
            icon_path_ico = os.path.join("frontend", "assets", "icons", "zerodown.ico")

            if os.path.exists(icon_path_png):
                icon_image = Image.open(icon_path_png)
                icon_photo = ImageTk.PhotoImage(icon_image)
                self.wm_iconphoto(True, icon_photo)

            if platform.system() == "Windows" and os.path.exists(icon_path_ico):
                self.iconbitmap(icon_path_ico)

        except Exception as e:
            print(f"Error setting icon: {e}") 

    def display_gif(self,label, gif_path, width, height, delay=40):
        gif = Image.open(gif_path)
        frames = []

        for i in range(gif.n_frames):
            gif.seek(i)
            frame = gif.copy().convert('RGBA')
            resized_frame = frame.resize((width, height), Image.LANCZOS)
            ctk_image = gui.CTkImage(light_image=resized_frame, dark_image=resized_frame, size=(width, height)) # use resized_frame
            frames.append(ctk_image)

        def update_frame(index):
            label.configure(image=frames[index])
            label.image = frames[index]
            self.after(delay, update_frame, (index + 1) % len(frames))

        update_frame(0)

    def fade_app(self):
        self.master.master.master.attributes("-alpha", 0.3)
    
    def unfade_app(self):
        self.master.master.master.attributes("-alpha", 1) 

    def on_close(self):
        self.unfade_app()
        self.destroy()