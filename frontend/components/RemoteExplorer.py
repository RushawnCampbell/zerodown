
from frontend.components.Popup import Popup
import tkinter as tk 
from tkinter import  ttk
from PIL import Image, ImageTk
import customtkinter as gui
from flask import jsonify
import requests

class RemoteExplorer(Popup):
    def __init__(self, master, title, endpoint_name):
        super().__init__(master, title)
        self.master =master
        self.endpoint_name = endpoint_name
        self.configure(fg_color="#2B2B2B")
        self.after(500, self.custom_set_pos)
        self.checkbox_vars = {}
        self.checked_items = {}  
        self.load_checkbox_images()
        self.create_three_column_layout()
        self.create_bottom_buttons()

    def custom_set_pos(self):
        self.set_window_position(900,450)

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

        # Column 1: Drive and Directory Tree
        self.drive_frame = gui.CTkFrame(self)
        self.drive_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.drive_frame.grid_columnconfigure(0, weight=1)
        self.drive_frame.grid_rowconfigure(0, weight=1)

        self.drive_tree = ttk.Treeview(master=self.drive_frame, yscrollcommand=self.on_scrollbar_drive, show="tree headings")
        self.drive_tree.grid(row=0, column=0, sticky="nsew")

        self.drive_scrollbar = gui.CTkScrollbar(master=self.drive_frame, orientation="vertical", command=self.drive_tree.yview)
        self.drive_scrollbar.grid(row=0, column=1, sticky="ns")

        self.drive_tree.configure(yscrollcommand=self.drive_scrollbar.set)
        self.drive_tree.heading("#0", text="Drives and Folders", anchor="w")
        self.build_drive_tree_from_lines()
        self.drive_tree.bind("<Button-1>", self.on_tree_click)

        # Column 2: Virtual Machines Tree
        self.vm_frame = gui.CTkFrame(self)
        self.vm_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
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
        self.app_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
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
        self.cancel_button.grid(row=0, column=0, padx=10, pady=5, sticky="ew") # Changed sticky to "ew"

        self.continue_button = gui.CTkButton(self.button_frame, text="Continue", command=self.continue_selection)
        self.continue_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew") # Changed sticky to "ew"

        self.grid_rowconfigure(1, weight=0) # Ensure the button frame doesn't resize the window vertically

    def cancel_selection(self):
        self.on_close()

    def continue_selection(self):
        self.master.directory_listing = self.checked_items
        print( self.master.directory_listing)
        self.master.backup_demand = self.get_backup_demand( self.master.directory_listing)
        self.master.browse_destination_button.configure(state='normal', fg_color="#1F6AA5")
        self.on_close()

    def on_scrollbar_drive(self, *args):
        self.drive_tree.yview(*args)

    def build_drive_tree_from_lines(self):
        tree_data = {}
        for line in self.master.directory_listing:
            parts = line.split("\\")
            drive = parts[0]
            if drive not in tree_data:
                tree_data[drive] = {}
            current_level = tree_data[drive]
            for part in parts[1:]:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]

        def insert_items(parent, data, path=""):
            for name, subdata in data.items():
                full_path = f"{path}\\{name}" if path else name
                full_path = full_path.rstrip('\r')
                item = self.drive_tree.insert(parent, "end", text=name, open=False, image=self.unchecked_image)
                self.checkbox_vars[item] = tk.BooleanVar(value=False)
                if subdata:
                    insert_items(item, subdata, full_path)

        for drive, data in tree_data.items():
            drive_item = self.drive_tree.insert("", "end", text=drive, open=False, image=self.unchecked_image)
            self.checkbox_vars[drive_item] = tk.BooleanVar(value=False)
            insert_items(drive_item, data)

    def build_vm_tree(self):
        root = self.vm_tree.insert("", "end", text="Virtual Machines", open=True)
        for vm in self.master.virtual_machines:
            item = self.vm_tree.insert(root, "end", text=vm, image=self.unchecked_image)
            self.checkbox_vars[item] = tk.BooleanVar(value=False)

    def build_app_tree(self):
        root = self.app_tree.insert("", "end", text="Applications", open=True)
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
                parent = tree.parent(item)
                path_components = [item_text]
                while parent:
                    parent_text = tree.item(parent, "text")
                    path_components.insert(0, parent_text)
                    parent = tree.parent(parent)
                full_path = "\\".join(path_components)
                full_path= full_path.rstrip('\r')

                if tree == self.drive_tree:
                    drive = full_path.split('\\')[0]
                    if drive not in self.checked_items:
                        self.checked_items[drive] = {}
                    self.checked_items[drive][full_path]=0
                elif tree == self.vm_tree:
                    if "Virtual Machines" not in self.checked_items:
                        self.checked_items["Virtual Machines"] = {}
                    self.checked_items["Virtual Machines"][item_text]=0
                elif tree == self.app_tree:
                    if "Applications" not in self.checked_items:
                        self.checked_items["Applications"] = {}
                    self.checked_items["Applications"][item_text]=0

            else:
                tree.item(item, image=self.unchecked_image)
                item_text = tree.item(item, "text")
                parent = tree.parent(item)
                path_components = [item_text]
                while parent:
                    parent_text = tree.item(parent, "text")
                    path_components.insert(0, parent_text)
                    parent = tree.parent(parent)
                full_path = "\\".join(path_components)
                full_path= full_path.rstrip('\r')

                if tree == self.drive_tree:
                    drive = full_path.split("\\")[0]
                    if drive in self.checked_items and full_path in self.checked_items[drive]:
                        del self.checked_items[drive][full_path]
                        if not self.checked_items[drive]:
                            del self.checked_items[drive]
                elif tree == self.vm_tree:
                    if "Virtual Machines" in self.checked_items and item_text in self.checked_items["Virtual Machines"]:
                        self.checked_items["Virtual Machines"].remove(item_text)
                        if not self.checked_items["Virtual Machines"]:
                            del self.checked_items["Virtual Machines"]
                elif tree == self.app_tree:
                    if "Applications" in self.checked_items and item_text in self.checked_items["Applications"]:
                        self.checked_items["Applications"].remove(item_text)
                        if not self.checked_items["Applications"]:
                            del self.checked_items["Applications"]

            self.drive_tree.update_idletasks()
            self.vm_tree.update_idletasks()
            self.app_tree.update_idletasks()

    def on_single_click(self, event):
        pass

    def get_backup_demand(self,jsondata):
        resource_url= f"http://127.0.0.1:8080/zeroapi/v1/endpoint/backupdemand/{self.endpoint_name}"
        zauth_token = self.master.master.retrieve_auth_token()
        zeroheaders = {"Authorization": f"Bearer {zauth_token}", "Content-Type": "application/json"}
        del zauth_token
        try:
            response = requests.post( resource_url, stream=True, headers=zeroheaders, json=jsondata)
            response.raise_for_status()
            directory_listing = response.json()
            self.directory_listing= directory_listing
        except requests.exceptions.RequestException as e:
            tk.messagebox.showerror("Fetch Error", f"Failed to obtain backup demand {e}")
            #return -1
        except Exception as e:
            print("ERROR IS",e)
            tk.messagebox.showerror("Fetch Error", f"An Application Error Occurred, report this to ZeroDown.")
            #return -1


    

