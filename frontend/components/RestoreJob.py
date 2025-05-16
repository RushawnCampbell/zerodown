import customtkinter as gui
import tkinter as tk
from tkinter import messagebox
import os, requests, platform, time
from PIL import Image, ImageTk

class RestoreJob(gui.CTkToplevel):
    """
    A custom top-level window (popup) for initiating and displaying the status of a restore job.
    It allows the user to select a restore point from a list.
    """
    def __init__(self, master, title, job_id, restore_points):
        """
        Initializes the RestoreJob popup.
        """
        super().__init__(master) # Initialize the CTkToplevel base class
        self.master = master # Store the master window
        self.job_id = job_id # Store the ID of the backup job to be restored
        self.restore_points = restore_points # Store the dictionary of available restore points
        self.volume_buttons = {} # Dictionary to store the buttons for each restore point
        self.gif_label_widget = None # Label widget to display the restore animation GIF
        self.scrollable_frame = None # Scrollable frame to hold the restore point buttons
        self.volume_label_text_widget = None # Label displaying "Choose An Available Restore Point"
        self.status_label_widget = None # Label to display the current restore status
        self.close_button_widget = None # Button to close the restore window
        self.gif_frames = [] # List to store individual frames of the restore GIF
        self.centering_frame = None # Frame to center the content

        self.after(300, self.set_icon) # Call set_icon after 300ms to set the window icon
        self.title(title) # Set the title of the popup window
        self.set_window_position(400, 400) # Set the initial size and position of the window
        self.transient(master) # Make the popup window dependent on the master window
        self.fade_app() # Fade out the main application window

        self.gif_path = os.path.join("frontend", "assets", "icons", "restore.gif") # Define the path to the restore animation GIF
        self.load_gif(width=200, height=200) # Load the GIF frames with specified width and height
        self.configure_body() # Configure the visual elements of the popup
    
    def configure_body(self):
        """
        Configures the appearance and layout of the popup window's body.
        """
        self.configure(fg_color="#FFFFFF") # Set the background color of the popup to white
        self.protocol("WM_DELETE_WINDOW", self.on_close) # Define what happens when the window's close button is pressed

        self.grid_rowconfigure(0, weight=1) # Configure the first row to expand vertically (for centering)
        self.grid_rowconfigure(1, weight=0) # Configure the second row (volumes label) to not expand
        self.grid_rowconfigure(2, weight=0) # Configure the third row (scrollable frame) to not expand initially
        self.grid_rowconfigure(3, weight=0) # Configure the fourth row (close button) to not expand
        self.grid_columnconfigure(0, weight=1) # Configure the first column to expand horizontally

        self.centering_frame = gui.CTkFrame(self, fg_color="transparent") # Create a transparent frame for centering content
        self.centering_frame.grid(row=0, column=0, sticky="nsew") # Place the centering frame, expanding in all directions
        self.centering_frame.grid_rowconfigure(0, weight=1) # Allow content within this frame to center vertically
        self.centering_frame.grid_columnconfigure(0, weight=1) # Allow content within this frame to center horizontally

        gif_label = gui.CTkLabel(self.centering_frame, text="") # Create a label to display the GIF
        gif_label.grid(row=0, column=0, pady=(0, 5)) # Place the GIF label with vertical padding
        self.gif_label_widget = gif_label # Store the GIF label widget
        self.gif_label_widget.grid_remove() # Initially hide the GIF label

        status_label = gui.CTkLabel(self.centering_frame, text="", text_color="gray") # Create a label for the status text
        status_label.grid(row=1, column=0, pady=(5, 10)) # Place the status label with vertical padding
        self.status_label_widget = status_label # Store the status label widget
        self.status_label_widget.grid_remove() # Initially hide the status label

        volume_label_text = gui.CTkLabel(self, text="Choose An Available Restore Point", text_color="#2B2B2B") # Create a label for the instruction text
        volume_label_text.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="ew") # Place the instruction label with padding and horizontal expansion
        self.volume_label_text_widget = volume_label_text # Store the instruction label widget

        self.scrollable_frame = gui.CTkScrollableFrame(self, fg_color="#000000") # Create a scrollable frame to hold the restore point buttons
        self.scrollable_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew") # Place the scrollable frame with padding and expansion
        self.scrollable_frame.grid_columnconfigure(0, weight=1) # Configure the column within the scrollable frame to expand

        button_index=0 # Initialize an index for placing buttons in the scrollable frame
        for restore_archive_str, restore_point_label in self.restore_points.items(): # Iterate through the restore points
            button = gui.CTkButton(self.scrollable_frame, text=restore_point_label, command=lambda ras=restore_archive_str, label=restore_point_label: self.confirm_restore(ras, label)) # Create a button for each restore point
            button.grid(row=button_index, column=0, padx=10, pady=(0, 10), sticky="ew") # Place the button in the scrollable frame
            self.volume_buttons[restore_point_label] = button # Store the button in the volume_buttons dictionary
            button_index+=1 # Increment the button index

        close_button = gui.CTkButton(self, text="Close", command=self.on_close) # Create a close button for the window
        close_button.grid(row=3, column=0, padx=10, pady=(10, 10), sticky="sew") # Place the close button with padding and bottom-east-west alignment
        self.close_button_widget = close_button # Store the close button widget

    def confirm_restore(self, ras, label):
        """
        Displays a confirmation dialog before initiating the restore process.
        If the user confirms, it updates the UI to show the restore animation and status.

        Args:
            ras (str): The restore archive string identifier.
            label (str): The user-friendly label of the restore point.
        """
        if messagebox.askyesno("Confirm Restore", f"Would you like to restore data as at '{label}'?"): # Show a confirmation dialog
            self.volume_label_text_widget.grid_remove() # Hide the "Choose An Available Restore Point" label
            self.scrollable_frame.grid_remove() # Hide the scrollable frame with the restore point buttons
            self.status_label_widget.configure(text=f"Restoring data from {label}...") # Update the status label
            self.status_label_widget.grid() # Show the status label
            self.play_gif(0) # Start playing the restore animation GIF
            self.gif_label_widget.grid() # Show the GIF label

            self.grid_rowconfigure(0, weight=1) # Ensure the centering frame expands
            self.grid_rowconfigure(1, weight=0) # Ensure other rows do not expand unnecessarily
            self.grid_rowconfigure(2, weight=0)
            self.grid_rowconfigure(3, weight=0)
            self.centering_frame.grid(row=0, column=0, sticky="nsew") # Ensure centering frame occupies the space

            resource_url= f"http://127.0.0.1:8080//zeroapi/v1/restore" # Define the API endpoint for initiating restore
            zauth_token = self.master.master.master.retrieve_auth_token() # Retrieve the authentication token
            zeroheaders = {"Authorization": f"Bearer {zauth_token}", "Content-Type": "application/json"} # Define headers for the API request
            del zauth_token # Delete the token from memory after use
            try:
                response = requests.post( resource_url, stream=True, headers=zeroheaders, json={"restore_point": ras, "job_id": self.job_id}) # Send a POST request to initiate restore
                response.raise_for_status() # Raise an exception for HTTP errors
                status= "response.json()" # Note: The response JSON is not currently processed
            except requests.exceptions.RequestException as e:
                tk.messagebox.showerror("Fetch Error", f"Failed to fetch {e}") # Show an error message if the API request fails

            except Exception as e:
                print("ERROR IS",e) # Print any other exception that occurs
                tk.messagebox.showerror("Fetch Error", f"An Application Error Occurred, report this to ZeroDown.") # Show a generic application error message


    def load_gif(self, width=200, height=200, delay=40):
        """
        Loads the frames of the GIF animation from the specified file path.

        """
        try:
            gif = Image.open(self.gif_path) # Open the GIF file using PIL
            self.gif_frames = [] # Initialize an empty list to store GIF frames
            for i in range(gif.n_frames): # Iterate through each frame of the GIF
                gif.seek(i) # Go to the i-th frame
                frame = gif.copy().convert('RGBA') # Create a copy of the current frame and convert it to RGBA
                resized_frame = frame.resize((width, height), Image.LANCZOS) # Resize the frame using LANCZOS resampling
                ctk_image = gui.CTkImage(light_image=resized_frame, dark_image=resized_frame, size=(width, height)) # Create a CTkImage object for both light and dark modes
                self.gif_frames.append(ctk_image) # Add the CTkImage frame to the list
        except FileNotFoundError:
            print(f"Error: GIF file not found at {self.gif_path}") # Print an error if the GIF file is not found

    def play_gif(self, frame_index):
        """
        Plays the loaded GIF animation by updating the image of the gif_label_widget.


        """
        if self.gif_frames: # Check if any GIF frames were loaded
            self.gif_label_widget.configure(image=self.gif_frames[frame_index]) # Update the GIF label with the current frame
            self.gif_label_widget.image = self.gif_frames[frame_index] # Keep a reference to the image object
            self.after(40, self.play_gif, (frame_index + 1) % len(self.gif_frames)) # Schedule the next frame to be displayed after a delay

    def set_window_position(self, window_width, window_height):
        """
        Sets the position of the popup window to the center of the screen.
        """
        screen_width = self.winfo_screenwidth() # Get the width of the entire screen
        screen_height = self.winfo_screenheight() # Get the height of the entire screen
        x = (screen_width - window_width) // 2 # Calculate the x-coordinate to center the window horizontally
        y = (screen_height - window_height) // 2 # Calculate the y-coordinate to center the window vertically

        self.geometry(f"{window_width}x{window_height}+{x}+{y}") # Set the geometry (size and position) of the window
        self.resizable(width=False, height=False) # Prevent the user from resizing the window

    def set_window_position_top_centered(self, window_width, window_height):
        """
        Sets the position of the popup window to the top center of the screen.

        """
        screen_width = self.winfo_screenwidth() # Get the width of the entire screen
        screen_height = self.winfo_screenheight() # Get the height of the entire screen
        x = (screen_width - window_width) // 2 # Calculate the x-coordinate to center the window horizontally
        y = 0 # Set the y-coordinate to the top of the screen

        self.geometry(f"{window_width}x{window_height}+{x}+{y}") # Set the geometry (size and position) of the window
        self.resizable(width=False, height=False) # Prevent the user from resizing the window

    def set_icon(self):
        """
        Sets the application icon for the popup window.
        It tries to load both PNG and ICO formats and sets the appropriate icon based on the platform and file existence.
        """
        try:
            icon_path_png = os.path.join("frontend", "assets", "icons", "zerodown.png") # Construct the path to the PNG icon
            icon_path_ico = os.path.join("frontend", "assets", "icons", "zerodown.ico") # Construct the path to the ICO icon

            if os.path.exists(icon_path_png): # Check if the PNG icon file exists
                icon_image = Image.open(icon_path_png) # Open the PNG image using PIL
                icon_photo = ImageTk.PhotoImage(icon_image) # Create a PhotoImage object from the PIL image
                self.wm_iconphoto(True, icon_photo) # Set the icon for the window manager

            if platform.system() == "Windows" and os.path.exists(icon_path_ico): # Check if the operating system is Windows and the ICO icon file exists
                self.iconbitmap(icon_path_ico) # Set the icon using the ICO file (for Windows)

        except Exception as e:
            print(f"Error setting icon: {e}") # Print an error message if any exception occurs during icon setting

    def fade_app(self):
        """
        Fades out the main application window.
        This is done by changing the alpha (transparency) attribute of the grandparent of this window.
        """
        self.master.master.master.attributes("-alpha", 0.3)

    def unfade_app(self):
        """
        Restores the opacity of the main application window.
        This is done by setting the alpha attribute of the grandparent of this window back to 1.
        """
        self.master.master.master.attributes("-alpha", 1)

    def on_close(self):
        """
        Handles the event when the popup window is closed.
        It unfades the main application window and then destroys the popup.
        """
        self.unfade_app() # Restore the opacity of the main application window
        self.destroy() # Destroy the RestoreJob popup window