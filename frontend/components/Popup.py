import customtkinter as gui
from PIL import Image, ImageTk
import os, platform, tkinter

class Popup(gui.CTkToplevel):
    def __init__(self, master, title):
        super().__init__(master)
        self.after(300, self.set_icon)
        self.title(title)
        self.set_window_position(430,300)
        self.transient(master)
        self.fade_app()
        self.configure(fg_color="#FFFFFF")

    def fade_app(self):
        self.master.master.attributes("-alpha", 0.3) 
    
    def unfade_app(self):
        self.master.master.attributes("-alpha", 1) 

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

    def on_close(self):
        self.unfade_app()
        self.destroy()

    def disable_close(self):
        pass


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