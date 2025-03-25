from frontend.components.Popup import Popup
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import customtkinter as gui
from flask import jsonify
import requests

class RemoteExplorer(Popup):
    def __init__(self, master, title, endpoint_name):
        super().__init__(master, title)
        self.master = master
        self.endpoint_name = endpoint_name
        self.configure(fg_color="#2B2B2B")
        self.after(500, self.custom_set_pos)
        self.checkbox_vars = {}
        self.checked_items = {}
        self.load_checkbox_images()
        self.create_three_column_layout()
        self.create_bottom_buttons()

    def custom_set_pos(self):
        self.set_window_position(900, 450)

    def load_checkbox_images(self):
        checked_image = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        for x in range(4, 12):
            for y in range(4, 12):
                checked_image.putpixel((x, y), (0, 0, 0, 255))

        unchecked_image = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        for x in range(4, 12):
            unchecked_image.putpixel((x, 4), (0, 0, 0, 255))
            unchecked_image.putpixel((x, 11), (0, 0, 0, 255))
            unchecked_image.putpixel((4, x), (0, 0, 0, 255))
            unchecked_image.putpixel((11, x), (0, 0, 0, 255))

        self.checked_image = ImageTk.PhotoImage(checked_image)
        self.unchecked_image = ImageTk.PhotoImage(unchecked_image)

    def create_three_column_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Column 1: Volume Tree
        self.vol_frame = gui.CTkFrame(self)
        self.vol_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew") # Changed column to 0
        self.vol_frame.grid_columnconfigure(0, weight=1)
        self.vol_frame.grid_rowconfigure(0, weight=1)

        self.vol_tree = ttk.Treeview(master=self.vol_frame, show="tree headings")
        self.vol_tree.grid(row=0, column=0, sticky="nsew")

        self.vol_scrollbar = gui.CTkScrollbar(master=self.vol_frame, orientation="vertical", command=self.vol_tree.yview)
        self.vol_scrollbar.grid(row=0, column=1, sticky="ns")

        self.vol_tree.configure(yscrollcommand=self.vol_scrollbar.set)
        self.vol_tree.heading("#0", text="Volumes", anchor="w")
        self.build_vol_tree()
        self.vol_tree.bind("<Button-1>", self.on_tree_click)

        # Column 2: Virtual Machines Tree
        self.vm_frame = gui.CTkFrame(self)
        self.vm_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew") # Changed column to 1
        self.vm_frame.grid_columnconfigure(0, weight=1)
        self.vm_frame.grid_rowconfigure(0, weight=1)

        self.vm_tree = ttk.Treeview(master=self.vm_frame, show="tree headings")
        self.vm_tree.grid(row=0, column=0, sticky="nsew")

        self.vm_scrollbar = gui.CTkScrollbar(master=self.vm_frame, orientation="vertical", command=self.vm_tree.yview)
        self.vm_scrollbar.grid(row=0, column=1, sticky="ns")

        self.vm_tree.configure(yscrollcommand=self.vm_scrollbar.set)
        self.vm_tree.heading("#0", text="Virtual Machines", anchor="w")
        self.build_vm_tree()
        self.vm_tree.bind("<Button-1>", self.on_tree_click)

        # Column 3: Applications Tree
        self.app_frame = gui.CTkFrame(self)
        self.app_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew") # Changed column to 2
        self.app_frame.grid_columnconfigure(0, weight=1)
        self.app_frame.grid_rowconfigure(0, weight=1)

        self.app_tree = ttk.Treeview(master=self.app_frame, show="tree headings")
        self.app_tree.grid(row=0, column=0, sticky="nsew")

        self.app_scrollbar = gui.CTkScrollbar(master=self.app_frame, orientation="vertical", command=self.app_tree.yview)
        self.app_scrollbar.grid(row=0, column=1, sticky="ns")

        self.app_tree.configure(yscrollcommand=self.app_scrollbar.set)
        self.app_tree.heading("#0", text="Applications", anchor="w")
        self.build_app_tree()
        self.app_tree.bind("<Button-1>", self.on_tree_click)

    def create_bottom_buttons(self):
        self.button_frame = gui.CTkFrame(self)
        self.button_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        self.cancel_button = gui.CTkButton(self.button_frame, text="Cancel Selection", command=self.cancel_selection)
        self.cancel_button.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.continue_button = gui.CTkButton(self.button_frame, text="Continue", command=self.continue_selection)
        self.continue_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        self.grid_rowconfigure(1, weight=0)

    def cancel_selection(self):
        self.on_close()

    def continue_selection(self):
        #self.master.volumes = self.checked_items
        for drives,size in self.checked_items['Volumes'].items():
            self.master.backup_demand += size
        print("DEMAND IS", self.master.backup_demand)
        self.master.browse_destination_button.configure(state='normal', fg_color="#1F6AA5")
        self.on_close()

    def on_scrollbar_drive(self, *args):
        pass # Removed as it seems unused in the current context

    def build_vol_tree(self):
        root = self.vol_tree.insert("", "end", text="Volumes", open=True)
        if hasattr(self.master, 'volumes') and self.master.volumes:
            for vol in self.master.volumes:
                item = self.vol_tree.insert(root, "end", text=vol, image=self.unchecked_image)
                self.checkbox_vars[item] = tk.BooleanVar(value=False)

    def build_vm_tree(self):
        root = self.vm_tree.insert("", "end", text="Virtual Machines", open=True)
        if hasattr(self.master, 'virtual_machines') and self.master.virtual_machines:
            for vm in self.master.virtual_machines:
                item = self.vm_tree.insert(root, "end", text=vm, image=self.unchecked_image)
                self.checkbox_vars[item] = tk.BooleanVar(value=False)

    def build_app_tree(self):
        root = self.app_tree.insert("", "end", text="Applications", open=True)
        if hasattr(self.master, 'applications') and self.master.applications:
            for app in self.master.applications:
                item = self.app_tree.insert(root, "end", text=app, image=self.unchecked_image)
                self.checkbox_vars[item] = tk.BooleanVar(value=False)

    def on_tree_click(self, event):
        tree = event.widget
        item = tree.identify_row(event.y)
        if item:
            self.toggle_checkbox(item, tree)

    def toggle_checkbox(self, item, tree):
        if item in self.checkbox_vars:
            current_state = self.checkbox_vars[item].get()
            self.checkbox_vars[item].set(not current_state)

            if self.checkbox_vars[item].get():
                tree.item(item, image=self.checked_image)
                item_text = tree.item(item, "text")

                if tree == self.vol_tree:
                    if "Volumes" not in self.checked_items:
                        self.checked_items["Volumes"] = {}
                    self.checked_items["Volumes"][item_text] = self.master.volumes_with_size[item_text]['UsedSpaceGB']
                elif tree == self.vm_tree:
                    if "Virtual Machines" not in self.checked_items:
                        self.checked_items["Virtual Machines"] = {}
                    self.checked_items["Virtual Machines"][item_text] = 0
                elif tree == self.app_tree:
                    if "Applications" not in self.checked_items:
                        self.checked_items["Applications"] = {}
                    self.checked_items["Applications"][item_text] = 0
            else:
                tree.item(item, image=self.unchecked_image)
                item_text = tree.item(item, "text")

                if tree == self.vol_tree:
                    if "Volumes" in self.checked_items and item_text in self.checked_items["Volumes"]:
                        del self.checked_items["Volumes"][item_text]
                        if not self.checked_items["Volumes"]:
                            del self.checked_items["Volumes"]
                elif tree == self.vm_tree:
                    if "Virtual Machines" in self.checked_items and item_text in self.checked_items["Virtual Machines"]:
                        del self.checked_items["Virtual Machines"][item_text]
                        if not self.checked_items["Virtual Machines"]:
                            del self.checked_items["Virtual Machines"]
                elif tree == self.app_tree:
                    if "Applications" in self.checked_items and item_text in self.checked_items["Applications"]:
                        del self.checked_items["Applications"][item_text]
                        if not self.checked_items["Applications"]:
                            del self.checked_items["Applications"]

            self.vol_tree.update_idletasks()
            self.vm_tree.update_idletasks()
            self.app_tree.update_idletasks()

    def on_single_click(self, event):
        pass