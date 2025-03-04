import customtkinter as gui
from PIL import Image, ImageTk

import os, platform, tkinter

class Popup(gui.CTkToplevel):
    def __init__(self, master, title):
        super().__init__(master)
        self.after(500, self.set_icon)
        self.title(title)
        self.set_window_position(400,300)
        self.transient(master)
        master.master.attributes("-alpha", 0.3) 
        self.configure(fg_color="#FFFFFF")
        self.protocol("WM_DELETE_WINDOW", self.on_close)


    def set_window_position(self, window_width, window_height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2  # Center horizontally
        y = (screen_height - window_height) // 2  # Center vertically

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
        self.master.master.attributes("-alpha", 1) 
        self.destroy()