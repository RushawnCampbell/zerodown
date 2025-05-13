import customtkinter as gui
import tkinter as tk
from tkinter import messagebox
import os, requests, platform, time
from PIL import Image, ImageTk

class RestoreJob(gui.CTkToplevel):
    def __init__(self, master, title, job_id, restore_points):
        super().__init__(master)
        self.master = master
        self.job_id = job_id
        self.restore_points = restore_points
        self.volume_buttons = {} 
        self.gif_label_widget = None
        self.scrollable_frame = None
        self.volume_label_text_widget = None
        self.status_label_widget = None
        self.close_button_widget = None
        self.gif_frames = []
        self.centering_frame = None

        self.after(300, self.set_icon)
        self.title(title)
        self.set_window_position(400, 400)
        self.transient(master)
        self.fade_app()

        self.gif_path = os.path.join("frontend", "assets", "icons", "restore.gif")
        self.load_gif(width=200, height=200) # Set desired width and height here
        self.configure_body()

    def configure_body(self):
        self.configure(fg_color="#FFFFFF")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.grid_rowconfigure(0, weight=1) # Center content area
        self.grid_rowconfigure(1, weight=0) # Volumes label
        self.grid_rowconfigure(2, weight=0) # Scrollable frame
        self.grid_rowconfigure(3, weight=0) # Close button
        self.grid_columnconfigure(0, weight=1)

        self.centering_frame = gui.CTkFrame(self, fg_color="transparent")
        self.centering_frame.grid(row=0, column=0, sticky="nsew")
        self.centering_frame.grid_rowconfigure(0, weight=1) # Center content in this frame
        self.centering_frame.grid_columnconfigure(0, weight=1)

        gif_label = gui.CTkLabel(self.centering_frame, text="")
        gif_label.grid(row=0, column=0, pady=(0, 5))
        self.gif_label_widget = gif_label
        self.gif_label_widget.grid_remove()

        status_label = gui.CTkLabel(self.centering_frame, text="", text_color="gray")
        status_label.grid(row=1, column=0, pady=(5, 10))
        self.status_label_widget = status_label
        self.status_label_widget.grid_remove()

        volume_label_text = gui.CTkLabel(self, text="Choose An Available Restore Point", text_color="#2B2B2B")
        volume_label_text.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="ew")
        self.volume_label_text_widget = volume_label_text

        self.scrollable_frame = gui.CTkScrollableFrame(self, fg_color="#000000")
        self.scrollable_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        for i, label in enumerate(self.restore_points):
            button = gui.CTkButton(self.scrollable_frame, text=label, command=lambda l=label: self.confirm_restore(l))
            button.grid(row=i, column=0, padx=10, pady=(0, 10), sticky="ew")
            self.volume_buttons[label] = button

        close_button = gui.CTkButton(self, text="Close", command=self.on_close)
        close_button.grid(row=3, column=0, padx=10, pady=(10, 10), sticky="sew")
        self.close_button_widget = close_button

    def confirm_restore(self, restore_point):
        if messagebox.askyesno("Confirm Restore", f"Would you like to restore data as at '{restore_point}'?"):
            self.volume_label_text_widget.grid_remove()
            self.scrollable_frame.grid_remove()
            self.status_label_widget.configure(text=f"Restoring data from {restore_point}...")
            self.status_label_widget.grid()
            self.play_gif(0)
            self.gif_label_widget.grid()

            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=0)
            self.grid_rowconfigure(2, weight=0)
            self.grid_rowconfigure(3, weight=0)
            self.centering_frame.grid(row=0, column=0, sticky="nsew")


            resource_url= f"http://127.0.0.1:8080//zeroapi/v1/backup/restore"
            zauth_token = self.master.master.retrieve_auth_token()
            zeroheaders = {"Authorization": f"Bearer {zauth_token}", "Content-Type": "application/json"}
            del zauth_token
            try:
                response = requests.get( resource_url, stream=True, headers=zeroheaders, json={"restore_point": restore_point, "job_id": self.job_id})
                response.raise_for_status()
                status= "response.json()"
            except requests.exceptions.RequestException as e:
                tk.messagebox.showerror("Fetch Error", f"Failed to fetch {e}")

            except Exception as e:
                print("ERROR IS",e)
                tk.messagebox.showerror("Fetch Error", f"An Application Error Occurred, report this to ZeroDown.")

    def start_restore_animation(self):
        pass

    def load_gif(self, width=200, height=200, delay=40):
        try:
            gif = Image.open(self.gif_path)
            self.gif_frames = []
            for i in range(gif.n_frames):
                gif.seek(i)
                frame = gif.copy().convert('RGBA')
                resized_frame = frame.resize((width, height), Image.LANCZOS)
                ctk_image = gui.CTkImage(light_image=resized_frame, dark_image=resized_frame, size=(width, height))
                self.gif_frames.append(ctk_image)
        except FileNotFoundError:
            print(f"Error: GIF file not found at {self.gif_path}")

    def play_gif(self, frame_index):
        if self.gif_frames:
            self.gif_label_widget.configure(image=self.gif_frames[frame_index])
            self.gif_label_widget.image = self.gif_frames[frame_index]
            self.after(40, self.play_gif, (frame_index + 1) % len(self.gif_frames))

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

    def fade_app(self):
        self.master.master.master.attributes("-alpha", 0.3)

    def unfade_app(self):
        self.master.master.master.attributes("-alpha", 1)

    def on_close(self):
        self.unfade_app()
        self.destroy()