import customtkinter as gui

class ToolBar(gui.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master=master
        self.configure(fg_color="#000000")
        self.configure(height=0)
        self.grid(row=1, column=0, padx=0, pady=0, sticky="ew")