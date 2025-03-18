import tkinter as tk
from tkinter import ttk

class DriveExplorerTkinter(tk.Tk):
    def __init__(self, directory_lines):
        super().__init__()
        self.title("Drive Explorer (Tkinter)")
        self.geometry("300x400")

        self.directory_lines = directory_lines
        self.create_treeview()

    def create_treeview(self):
        # Create a frame to hold both the treeview and the scrollbar
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create the treeview
        self.tree = ttk.Treeview(master=frame, yscrollcommand=self.on_scrollbar)
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Create the scrollbar
        self.scrollbar = ttk.Scrollbar(master=frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Configure the treeview to use the scrollbar
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Configure row and column weights to make the treeview expand
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        self.tree.heading("#0", text="Drives and Folders", anchor="w")

        self.build_tree_from_lines()

        self.tree.bind("<Button-1>", self.on_single_click)

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
                item = self.tree.insert(parent, "end", text=name, open=False)
                if subdata:
                    insert_items(item, subdata, full_path)

        for drive, data in tree_data.items():
            drive_item = self.tree.insert("", "end", text=drive, open=False)
            insert_items(drive_item, data)

    def on_single_click(self, event):
        item = self.tree.focus()
        if item:
            item_text = self.tree.item(item, "text")
            print(f"Single-clicked on: {item_text}")

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
        "C:\\VeryLongFolder1\\VeryLongSubfolderA\\VeryLongSubSubfolder1\\VeryLongSubSubSubfolderA",
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

    app = DriveExplorerTkinter(directory_lines)
    app.mainloop()