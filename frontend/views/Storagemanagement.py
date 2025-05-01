import customtkinter as gui, traceback, json, requests, tkinter as tk
from PIL import Image
from frontend.components.RemoteExplorer import RemoteExplorer
from frontend.components.JobStatus import JobStatus
from frontend.components.ScheduleJob import ScheduleJob

class Storagemanagement(gui.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master.title("ZeroDown: Manage Endpoint")
        self.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")