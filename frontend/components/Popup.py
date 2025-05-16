import customtkinter as gui
from PIL import Image, ImageTk
import os, platform, tkinter

class Popup(gui.CTkToplevel):
    """
    A custom top-level window (popup) built using customtkinter.
    It provides common functionalities like setting icon, window position, and fading effects.
    """
    def __init__(self, master, title):
        """
        Initializes the Popup window.
        """
        super().__init__(master) # Initialize the CTkToplevel base class
        self.after(300, self.set_icon) # Call the set_icon method after a delay of 300 milliseconds
        self.title(title) # Set the title of the popup window
        self.set_window_position(430,300) # Set the initial position and size of the window
        self.transient(master) # Make the popup window dependent on the master window
        self.fade_app() # Initiate the fading effect on the main application window
        self.configure(fg_color="#FFFFFF") # Set the background color of the popup window to white

    def fade_app(self):
        """
        Fades out the main application window.
        This is done by changing the alpha (transparency) attribute of the master's master.
        """
        self.master.master.attributes("-alpha", 0.3)

    def unfade_app(self):
        """
        Restores the opacity of the main application window.
        This is done by setting the alpha attribute of the master's master back to 1.
        """
        self.master.master.attributes("-alpha", 1)

    def set_window_position(self, window_width, window_height):
        """
        Sets the position of the popup window to the center of the screen.

        Args:
            window_width (int): The desired width of the popup window.
            window_height (int): The desired height of the popup window.
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

        Args:
            window_width (int): The desired width of the popup window.
            window_height (int): The desired height of the popup window.
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

    def on_close(self):
        """
        Handles the event when the popup window is closed (e.g., by clicking the close button).
        It unfades the main application and then destroys the popup window.
        """
        self.unfade_app() # Restore the opacity of the main application window
        self.destroy() # Destroy the popup window

    def disable_close(self):
        """
        A placeholder method intended to disable the default close behavior of the window.
        Currently, it does nothing.
        """
        pass


    def display_gif(self,label, gif_path, width, height, delay=40):
        """
        Displays an animated GIF on a given customtkinter label.

        Args:
            label (customtkinter.CTkLabel): The label widget where the GIF will be displayed.
            gif_path (str): The path to the GIF file.
            width (int): The desired width of the displayed GIF.
            height (int): The desired height of the displayed GIF.
            delay (int, optional): The delay (in milliseconds) between frames. Defaults to 40.
        """
        gif = Image.open(gif_path) # Open the GIF file using PIL
        frames = [] # Initialize an empty list to store individual frames of the GIF

        for i in range(gif.n_frames): # Iterate through each frame of the GIF
            gif.seek(i) # Go to the i-th frame
            frame = gif.copy().convert('RGBA') # Create a copy of the current frame and convert it to RGBA format
            resized_frame = frame.resize((width, height), Image.LANCZOS) # Resize the frame to the desired width and height using LANCZOS resampling
            ctk_image = gui.CTkImage(light_image=resized_frame, dark_image=resized_frame, size=(width, height)) # Create a CTkImage object from the resized frame for both light and dark modes
            frames.append(ctk_image) # Add the CTkImage object to the list of frames

        def update_frame(index):
            """
            Updates the image displayed on the label with the frame at the given index.
            It then schedules the next frame update after the specified delay.

            Args:
                index (int): The index of the frame to display.
            """
            label.configure(image=frames[index]) # Configure the label to display the current frame
            label.image = frames[index] # Keep a reference to the image object to prevent garbage collection
            self.after(delay, update_frame, (index + 1) % len(frames)) # Schedule the update_frame function to be called again after the delay, with the next frame index (wrapping around if it's the last frame)

        update_frame(0) # Start the GIF animation by displaying the first frame