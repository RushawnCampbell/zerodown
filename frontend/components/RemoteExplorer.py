from frontend.components.Popup import Popup
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import customtkinter as gui

class RemoteExplorer(Popup):
    """
    A popup window for exploring and selecting remote objects (volumes or virtual machines).
    It displays the objects in a two-column treeview with checkboxes for selection.
    Inherits from the Popup class for basic popup functionalities.
    """
    def __init__(self, master, title, object_name, object_type, operation):
        """
        Initializes the RemoteExplorer popup.
        """
        
        super().__init__(master, title) # Initialize the Popup base class
        self.master = master # Store the master window
        self.object_name = object_name # Store the name of the main object
        self.object_type = object_type # Store the type of objects being explored
        self.operation = operation # Store the operation being performed
        self.configure(fg_color="#2B2B2B") # Set the background color of the popup
        self.after(500, self.custom_set_pos) # Call custom_set_pos after 500ms to set the window position
        self.checkbox_vars = {} # Dictionary to store the Tkinter BooleanVar for each checkbox
        self.checked_items = {} # Dictionary to store the items that have been checked
        self.load_checkbox_images() # Load the images for checked and unchecked checkboxes
        self.create_two_column_layout() # Create the two-column layout for volumes and VMs
        self.create_bottom_buttons() # Create the "Cancel" and "Continue" buttons at the bottom

        # Conditional layout adjustment for storage backup operation
        if self.object_type == "storage" and self.operation == "backup":
            self.vm_frame.grid_forget() # Hide the virtual machine frame
            self.grid_columnconfigure(1, weight=0) # Remove weight from the second column
            self.grid_columnconfigure(0, weight=1) # Force the first column to take full width
            self.vol_frame.grid(columnspan=2) # Make the volume frame span both columns

    def custom_set_pos(self):
        """
        Sets the custom position and size of the window.
        Calls the set_window_position method with specific dimensions.
        """
        self.set_window_position(900, 450) # Set the window size to 900x450 and center it

    def load_checkbox_images(self):
        """
        Creates and loads the images for checked and unchecked checkboxes.
        Uses PIL to draw simple checkbox visuals.
        """
        checked_image = Image.new("RGBA", (16, 16), (0, 0, 0, 0)) # Create a transparent image for the checked state
        for x in range(4, 12): # Draw a filled square for the checked state
            for y in range(4, 12):
                checked_image.putpixel((x, y), (0, 0, 0, 255))

        unchecked_image = Image.new("RGBA", (16, 16), (0, 0, 0, 0)) # Create a transparent image for the unchecked state
        for x in range(4, 12): # Draw the border of a square for the unchecked state
            unchecked_image.putpixel((x, 4), (0, 0, 0, 255))
            unchecked_image.putpixel((x, 11), (0, 0, 0, 255))
            unchecked_image.putpixel((4, x), (0, 0, 0, 255))
            unchecked_image.putpixel((11, x), (0, 0, 0, 255))

        self.checked_image = ImageTk.PhotoImage(checked_image) # Convert the PIL checked image to a Tkinter PhotoImage
        self.unchecked_image = ImageTk.PhotoImage(unchecked_image) # Convert the PIL unchecked image to a Tkinter PhotoImage

    def create_two_column_layout(self):
        """
        Creates a two-column layout within the popup to display volumes and virtual machines in separate treeviews.
        """
        self.grid_columnconfigure(0, weight=1) # Configure the first column to expand
        self.grid_columnconfigure(1, weight=1) # Configure the second column to expand
        self.grid_rowconfigure(0, weight=1) # Configure the first row to expand

        # Column 1: Volume Tree
        self.vol_frame = gui.CTkFrame(self) # Create a frame to hold the volume tree
        self.vol_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew") # Place the volume frame in the first column, expanding in all directions
        self.vol_frame.grid_columnconfigure(0, weight=1) # Configure the column within the volume frame to expand
        self.vol_frame.grid_rowconfigure(0, weight=1) # Configure the row within the volume frame to expand

        self.vol_tree = ttk.Treeview(master=self.vol_frame, show="tree headings") # Create a Treeview widget to display volumes
        self.vol_tree.grid(row=0, column=0, sticky="nsew") # Place the volume tree, expanding in all directions

        self.vol_scrollbar = gui.CTkScrollbar(master=self.vol_frame, orientation="vertical", command=self.vol_tree.yview) # Create a vertical scrollbar for the volume tree
        self.vol_scrollbar.grid(row=0, column=1, sticky="ns") # Place the scrollbar to the right of the volume tree, expanding vertically

        self.vol_tree.configure(yscrollcommand=self.vol_scrollbar.set) # Link the volume tree's vertical scroll to the scrollbar
        self.vol_tree.heading("#0", text="Volumes", anchor="w") # Set the heading text for the volume tree
        self.build_vol_tree() # Populate the volume tree with data
        self.vol_tree.bind("<Button-1>", self.on_tree_click) # Bind a left mouse click event to the tree

        # Column 2: Virtual Machines Tree
        self.vm_frame = gui.CTkFrame(self) # Create a frame to hold the virtual machine tree
        self.vm_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew") # Place the VM frame in the second column, expanding in all directions
        self.vm_frame.grid_columnconfigure(0, weight=1) # Configure the column within the VM frame to expand
        self.vm_frame.grid_rowconfigure(0, weight=1) # Configure the row within the VM frame to expand

        self.vm_tree = ttk.Treeview(master=self.vm_frame, show="tree headings") # Create a Treeview widget to display virtual machines
        self.vm_tree.grid(row=0, column=0, sticky="nsew") # Place the VM tree, expanding in all directions

        self.vm_scrollbar = gui.CTkScrollbar(master=self.vm_frame, orientation="vertical", command=self.vm_tree.yview) # Create a vertical scrollbar for the VM tree
        self.vm_scrollbar.grid(row=0, column=1, sticky="ns") # Place the scrollbar to the right of the VM tree, expanding vertically

        self.vm_tree.configure(yscrollcommand=self.vm_scrollbar.set) # Link the VM tree's vertical scroll to the scrollbar
        self.vm_tree.heading("#0", text="Virtual Machines", anchor="w") # Set the heading text for the VM tree
        self.build_vm_tree() # Populate the VM tree with data
        self.vm_tree.bind("<Button-1>", self.on_tree_click) # Bind a left mouse click event to the tree

    def create_bottom_buttons(self):
        """
        Creates the "Cancel Selection" and "Continue" buttons at the bottom of the popup.
        """
        self.button_frame = gui.CTkFrame(self) # Create a frame to hold the buttons
        self.button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew") # Place the button frame at the bottom, spanning both columns
        self.button_frame.grid_columnconfigure(0, weight=1) # Configure the first column within the button frame to expand
        self.button_frame.grid_columnconfigure(1, weight=1) # Configure the second column within the button frame to expand

        self.cancel_button = gui.CTkButton(self.button_frame, text="Cancel Selection", command=self.cancel_selection) # Create the cancel button
        self.cancel_button.grid(row=0, column=0, padx=10, pady=5, sticky="ew") # Place the cancel button in the first column, expanding horizontally

        self.continue_button = gui.CTkButton(self.button_frame, text="Continue", command=self.continue_selection) # Create the continue button
        self.continue_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew") # Place the continue button in the second column, expanding horizontally

        self.grid_rowconfigure(1, weight=0) # Ensure the button row does not expand vertically

    def cancel_selection(self):
        """
        Handles the action when the "Cancel Selection" button is clicked.
        It clears the selected volumes in the master window and closes the popup.
        """
        self.master.volumes = [] # Clear the volumes list in the master window
        self.on_close() # Close the popup window

    def continue_selection(self):
        """
        Handles the action when the "Continue" button is clicked.
        It processes the selected volumes or VMs based on the object type and operation.
        Updates relevant attributes in the master window and closes the popup.
        """
        if self.object_type == 'endpoint': # If the selected objects are from an endpoint
            for drive, size in self.checked_items['Volumes'].items(): # Iterate through the checked volumes and their sizes
                self.master.backup_demand += size # Add the size of the selected volume to the total backup demand in the master
                self.master.selected_endpoint_info = self.checked_items # Store the checked items in the master
                self.master.storage_node_dropdown.configure(state="normal", fg_color="#FFF", border_color="#FFF", dropdown_fg_color="#FFFFFF", dropdown_text_color="#000000") # Enable and style the storage node dropdown in the master
                print("CHECKED ENDPOINT VOLUME",  self.master.selected_endpoint_info) # Print the selected endpoint information

        elif self.object_type == 'storage': # If the selected objects are storage volumes
            for drive, size in self.checked_items['Volumes'].items(): # Iterate through the checked volumes and their sizes
                self.master.available_storage_size += size # Add the size of the selected storage to the available storage size in the master
                self.master.schedule_backup_button.configure(state="normal", fg_color="#1F6AA5") # Enable and style the schedule backup button in the master
                self.master.backup_now_button.configure(state="normal", fg_color="#1fa59d") # Enable and style the backup now button in the master
                self.master.selected_storage_info = self.checked_items # Store the checked items in the master
                print("CHECKED STORAGE",  self.master.selected_storage_info) # Print the selected storage information
        self.master.volumes = [] # Clear the volumes list in the master window
        self.on_close() # Close the popup window

    def on_scrollbar_drive(self, *args):
        """
        A placeholder method for handling scrollbar events (currently does nothing).
        """
        pass

    def build_vol_tree(self):
        """
        Populates the volume treeview with the volumes available in the master window.
        It inserts each volume as a child of the root node with an unchecked checkbox image.
        """
        root = self.vol_tree.insert("", "end", text="Volumes", open=True) # Insert the root node for volumes
        if hasattr(self.master, 'volumes') and self.master.volumes: # Check if the master has a 'volumes' attribute and it's not empty
            for vol in self.master.volumes: # Iterate through the list of volumes
                item = self.vol_tree.insert(root, "end", text=vol, image=self.unchecked_image) # Insert each volume as a child with the unchecked image
                self.checkbox_vars[item] = tk.BooleanVar(value=False) # Create a BooleanVar for each volume and associate it with the item

    def build_vm_tree(self):
        """
        Populates the virtual machine treeview with the VMs available in the master window.
        It inserts each VM as a child of the root node with an unchecked checkbox image.
        """
        root = self.vm_tree.insert("", "end", text="Virtual Machines", open=True) # Insert the root node for virtual machines
        if hasattr(self.master, 'virtual_machines') and self.master.virtual_machines: # Check if the master has a 'virtual_machines' attribute and it's not empty
            for vm in self.master.virtual_machines: # Iterate through the list of virtual machines
                item = self.vm_tree.insert(root, "end", text=vm, image=self.unchecked_image) # Insert each VM as a child with the unchecked image
                self.checkbox_vars[item] = tk.BooleanVar(value=False) # Create a BooleanVar for each VM and associate it with the item

    def on_tree_click(self, event):
        """
        Handles the left mouse click event on either of the treeviews.
        It identifies the clicked item and toggles its checkbox state.
        """
        tree = event.widget # Get the treeview widget that triggered the event
        item = tree.identify_row(event.y) # Get the item ID of the clicked row
        if item: # If an item was clicked
            self.toggle_checkbox(item, tree) # Call the toggle_checkbox method for the clicked item and tree

    def toggle_checkbox(self, item, tree):
        """
        Toggles the checkbox state of a given item in a treeview.
        It updates the checkbox image and the checked_items dictionary accordingly.

        Args:
            item: The item ID in the treeview.
            tree: The treeview widget (either vol_tree or vm_tree).
        """
        if item in self.checkbox_vars: # Check if the item has an associated checkbox variable
            current_state = self.checkbox_vars[item].get() # Get the current state of the checkbox
            self.checkbox_vars[item].set(not current_state) # Toggle the state of the checkbox variable

            if self.checkbox_vars[item].get(): # If the checkbox is now checked
                tree.item(item, image=self.checked_image) # Set the image to the checked image
                item_text = tree.item(item, "text") # Get the text of the item

                if tree == self.vol_tree: # If the volume tree was clicked
                    if "Volumes" not in self.checked_items: # Initialize the "Volumes" key if it doesn't exist
                        self.checked_items["Volumes"] = {}

                    if self.object_type == "endpoint": # If exploring endpoint volumes
                        self.checked_items["Volumes"][item_text] = self.master.volumes_with_size[item_text]['UsedSpaceGB'] # Store the used space of the selected volume

                    if self.object_type == "storage": # If exploring storage volumes
                        self.checked_items["Volumes"][item_text] = self.master.volumes_with_size[item_text]['AvailableSpaceGB'] # Store the available space of the selected volume

                elif tree == self.vm_tree: # If the virtual machine tree was clicked
                    if "Virtual Machines" not in self.checked_items: # Initialize the "Virtual Machines" key if it doesn't exist
                        self.checked_items["Virtual Machines"] = {}
                    self.checked_items["Virtual Machines"][item_text] = 0 # Store the selected VM (size is 0 for now)
            else: # If the checkbox is now unchecked
                tree.item(item, image=self.unchecked_image) # Set the image to the unchecked image
                item_text = tree.item(item, "text") # Get the text of the item

                if tree == self.vol_tree: # If the volume tree was clicked
                    if "Volumes" in self.checked_items and item_text in self.checked_items["Volumes"]: # If the volume is in the checked items
                        del self.checked_items["Volumes"][item_text] # Remove the volume from the checked items
                        if not self.checked_items["Volumes"]: # If no volumes are left
                            del self