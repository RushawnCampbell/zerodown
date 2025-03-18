import customtkinter as ctk
from tkinter import ttk
from PIL import Image, ImageTk
import tkinter as tk  # Import tkinter explicitly for BooleanVar

class DriveExplorerCustomTkinter(ctk.CTk):
    def __init__(self, directory_lines):
        super().__init__()
        self.title("Drive Explorer (CustomTkinter)")
        self.geometry("300x400")

        self.directory_lines = directory_lines
        self.checkbox_vars = {}
        self.checked_items = set()
        self.load_checkbox_images()
        self.create_treeview()

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

    def create_treeview(self):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(master=frame, yscrollcommand=self.on_scrollbar, show="tree headings")
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ctk.CTkScrollbar(master=frame, orientation="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree.configure(yscrollcommand=self.scrollbar.set)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        self.tree.heading("#0", text="Drives and Folders", anchor="w")

        self.build_tree_from_lines()

        self.tree.bind("<Button-1>", self.on_tree_click)
        self.tree.bind("<Button-3>", self.on_right_click)

    def on_scrollbar(self, *args):
        self.tree.yview(*args)

    def build_tree_from_lines(self):
        tree_data = {}
        for line in self.directory_lines:
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
                item = self.tree.insert(parent, "end", text=name, open=False, image=self.unchecked_image)
                self.checkbox_vars[item] = tk.BooleanVar(value=False) # Corrected: using tk.BooleanVar
                if subdata:
                    insert_items(item, subdata, full_path)

        for drive, data in tree_data.items():
            drive_item = self.tree.insert("", "end", text=drive, open=False, image=self.unchecked_image)
            self.checkbox_vars[drive_item] = tk.BooleanVar(value=False) # Corrected: using tk.BooleanVar
            insert_items(drive_item, data)

    def on_tree_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.toggle_checkbox(item)

    def on_right_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            print(f"Right-clicked on item: {self.tree.item(item, 'text')}")

    def toggle_checkbox(self, item):
        if item in self.checkbox_vars:
            current_state = self.checkbox_vars[item].get()
            self.checkbox_vars[item].set(not current_state)

            if self.checkbox_vars[item].get():
                self.tree.item(item, image=self.checked_image)
                self.checked_items.add(item)
            else:
                self.tree.item(item, image=self.unchecked_image)
                if item in self.checked_items:
                    self.checked_items.remove(item)

            self.tree.update_idletasks()
            print(f"Item: {self.tree.item(item, 'text')}, Checked: {self.checkbox_vars[item].get()}")
            print(f"Checked Items: {self.checked_items}")

    def on_single_click(self, event):
        pass

if __name__ == "__main__":
    directory_lines = [
        "C:\\Folder1",
        "C:\\Folder1\\SubfolderA",
        "C:\\Folder1\\SubfolderA\\SubSubfolder1",
        "C:\\Folder1\\SubfolderB",
        "C:\\Folder2",
        "C:\\Folder2\\AnotherSubfolder",
        "D:\\AnotherDriveFolder",
        "D:\\AnotherDriveFolder\\SubDir",
        "C:\\VeryLongFolder1\\VeryLongSubfolderA\\VeryLongSubSubfolder1\\VeryLongSubSubSubfolderA\\VeryLongSubSubSubfolderB\\VeryLongSubSubSubfolderC",
        "C:\\VeryLongFolder1\\VeryLongSubfolderB\\VeryLongSubSubfolder2\\VeryLongSubSubSubfolderB",
        "D:\\AnotherVeryLongDriveFolder\\AnotherVeryLongSubDir\\AnotherVeryLongSubSubDir",
        "E:\\AnotherDriveFolder",
        "F:\\AnotherDriveFolder",
        "G:\\AnotherDriveFolder",
        "H:\\AnotherDriveFolder",
        "I:\\AnotherDriveFolder",
        "J:\\AnotherDriveFolder",
        "K:\\AnotherDriveFolder",
        "L:\\AnotherDriveFolder",
        "M:\\AnotherDriveFolder",
    ]

    app = DriveExplorerCustomTkinter(directory_lines)
    app.mainloop()