import customtkinter as gui
from PIL import Image
import os

class ToolBar(gui.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master=master
        self.configure(fg_color="#000000")
        self.grid(row=1, column=0, padx=0, pady=0, sticky="ew")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
   
        self.menuimage = Image.open(os.path.join("frontend","assets", "icons", "menu.png"))
        self.ctk_image1 = gui.CTkImage(light_image=self.menuimage, dark_image=self.menuimage, size=(20, 20))
        self.menu1 = gui.CTkButton(self, image=self.ctk_image1,hover_color="#2B2B2B",text="")
        self.menu1.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.menu1.configure(fg_color="#000000")
        
        self.menuimage2 = Image.open(os.path.join("frontend","assets", "icons", "home.png"))
        self.ctk_image2 = gui.CTkImage(light_image=self.menuimage2, dark_image=self.menuimage2, size=(20, 20))
        self.menu2 = gui.CTkButton(self, image=self.ctk_image2, hover_color="#2B2B2B", text="",command=self.master.route_home)
        self.menu2.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.menu2.configure(fg_color="#000000")

        self.menuimage3 = Image.open(os.path.join("frontend","assets", "icons", "logout.png"))
        self.ctk_image3 = gui.CTkImage(light_image=self.menuimage3, dark_image=self.menuimage3, size=(20, 20))
        self.menu3 = gui.CTkButton(self, image=self.ctk_image3, hover_color="#2B2B2B", text="")
        self.menu3.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        self.menu3.configure(fg_color="#000000")


