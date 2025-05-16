import customtkinter as gui
import tkinter as tk
import os, requests
import time
from frontend.components.Popup import Popup
from PIL import Image

class JobStatus(Popup):
    """
    A popup window that displays the status of a backup job.
    Inherits from the Popup class for basic popup functionality.
    """
    def __init__(self, master, title, total_storage_volumes, job_id):
        """
        Initializes the JobStatus popup.

        Args:
            master: The parent window.
            title (str): The title of the popup window.
            total_storage_volumes (int): The total number of storage volumes being backed up.
            job_id (str): The ID of the backup job.
        """
        super().__init__(master, title) # Initialize the Popup base class
        self.total_storage_volumes = total_storage_volumes # Store the total number of storage volumes
        self.num_success = 0 # Initialize the count of successfully backed up volumes
        self.num_error = 0 # Initialize the count of volumes with errors during backup
        self.vol_with_success = [] # Initialize a list to store the names/IDs of successfully backed up volumes
        self.vol_with_error = [] # Initialize a list to store the names/IDs of volumes with backup errors
        self.job_id = job_id # Store the ID of the backup job
        self.master = master # Store the master window
        self.status_label= None # Initialize a label to display the overall status
        self.is_complete = False # Flag to indicate if the backup job is complete
        self.configure_body() # Configure the visual elements of the popup
        self.monitor_status() # Start monitoring the backup job status

    def configure_body(self):
        """
        Configures the appearance and behavior of the popup window's body.
        """
        self.configure(fg_color="#FFFFFF") # Set the background color of the popup
        self.protocol("WM_DELETE_WINDOW", self.on_close) # Define what happens when the window's close button is pressed (call self.on_close)

        self.rowconfigure(0, weight=1) # Configure the first row to expand vertically

        main_frame = gui.CTkFrame(self, fg_color="transparent") # Create a transparent frame to hold the content
        main_frame.pack(expand=True) # Pack the main frame to expand and fill the popup

        gif_label = gui.CTkLabel(main_frame, text="") # Create a label to display a GIF
        gif_label.pack(pady=(0, 5)) # Pack the GIF label with vertical padding

        status_text = f"Backing up to 1 of {self.total_storage_volumes} Storage Volumes " # Initial status text
        self.status_label = gui.CTkLabel(main_frame, text=status_text) # Create a label for the status text
        self.status_label.pack(pady=(5, 0)) # Pack the status label with vertical padding
        self.status_label.configure(text_color="#1fa59d") # Set the text color of the status label

        self.volumes_backed_up_label = gui.CTkLabel(main_frame, text=f"Storage Volumes:{self.num_success}") # Create a label to display the number of successful backups
        self.volumes_backed_up_label.pack(pady=(0, 5)) # Pack the successful backups label with vertical padding
        self.volumes_backed_up_label.configure(text_color="#1F6AA5") # Set the text color of the successful backups label

        self.failed_volumes_label = gui.CTkLabel(main_frame, text=f"Failed Storage Volumes: {self.num_error}") # Create a label to display the number of failed backups
        self.failed_volumes_label.pack(pady=(0, 5)) # Pack the failed backups label with vertical padding
        self.failed_volumes_label.configure(text_color="#1F6AA5") # Set the text color of the failed backups label

        gif_path = os.path.join("frontend", "assets", "icons", "backing_up.gif") # Construct the path to the backup GIF
        self.display_gif(gif_label, gif_path, 100, 100) # Display the GIF in the specified label with dimensions 100x100

        self.close_button = gui.CTkButton(self, text="Close(Backup will continue to run)", command=self.on_close) # Create a close button
        self.close_button.configure(state="normal", fg_color="#1fa59d") # Configure the state and background color of the close button
        self.close_button.pack(pady=20) # Pack the close button with vertical padding

    def get_status(self):
        """
        Retrieves the current status of the backup job from the backend API.

        Returns:
            dict: A dictionary containing lists of successful and failed volume IDs.
                  Returns {"success": [], "error": []} in case of an error during the API request.
        """
        resource_url= f"http://127.0.0.1:8080/zeroapi/v1/backup/get_status" # Define the API endpoint for getting backup status
        zauth_token = self.master.master.retrieve_auth_token() # Retrieve the authentication token from the main application
        zeroheaders = {"Authorization": f"Bearer {zauth_token}", "Content-Type": "application/json"} # Define the headers for the API request, including the authorization token
        try:
            response = requests.post( resource_url, stream=True, headers=zeroheaders, json={"job_id" : self.job_id}) # Make a POST request to the API endpoint with the job ID in the JSON body
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            data = response.json() # Parse the JSON response
            return {"success": data.get("success"), "error" : data.get("error")} # Return a dictionary containing lists of successful and errored volumes
        except requests.exceptions.RequestException as e:
            print(f"Error fetching status: {e}") # Print an error message if the API request fails
            return {"success": [], "error" : []} # Return empty lists for success and error in case of an error

    def vol_report(self, vol_list):
        """
        Formats a list of volume IDs into a comma-separated string.

        Args:
            vol_list (list): A list of volume IDs (strings).

        Returns:
            str: A comma-separated string of volume IDs.
        """
        vol_str = "" # Initialize an empty string
        for vol in vol_list: # Iterate through the list of volumes
            if vol_list.index(vol) == 0: # If it's the first volume in the list
                vol_str += f"{vol}" # Add the volume ID to the string
            else: # If it's not the first volume
                vol_str += f",{vol}" # Add a comma and then the volume ID to the string
        return vol_str # Return the formatted string

    def monitor_status(self):
        """
        Continuously monitors the backup job status and updates the UI.
        It fetches the status from the backend API at regular intervals.
        """
        if not self.is_complete: # Check if the backup job is not yet complete
            status = self.get_status() # Get the current status of the backup job
            self.vol_with_success.extend(status['success']) # Add new successful volumes to the list
            self.vol_with_error.extend(status['error']) # Add new errored volumes to the list
            self.num_success = len(set(self.vol_with_success)) # Update the count of unique successful volumes
            self.num_error = len(set(self.vol_with_error)) # Update the count of unique errored volumes
            if self.num_success + self.num_error == self.total_storage_volumes: # Check if all volumes have been processed
                self.is_complete = True # Set the completion flag to True

                if self.num_success == self.total_storage_volumes and self.num_error == 0: # If all volumes were backed up successfully
                    self.status_label.configure(text="All Volumes Backed Up!", text_color="#1fa59d") # Update the status label
                    self.failed_volumes_label.configure(text=f"Failed Volumes: {self.num_error}") # Update the failed volumes label
                    success_vol_str = self.vol_report(self.vol_with_success) # Format the list of successful volumes
                    self.volumes_backed_up_label.configure(text=f"Volumes Backed Up: {success_vol_str}", text_color="#1fa59d") # Update the backed up volumes label

                elif self.num_success == 0 and self.num_error >= 1 : # If all volumes failed to backup
                    self.status_label.configure(text="All Volumes Failed To Backup!", text_color="#cc3300") # Update the status label
                    self.volumes_backed_up_label.configure(text=f"Volumes Backed Up: {self.num_success}", text_color="#1fa59d") # Update the backed up volumes label
                    failed_vol_str = self.vol_report(self.vol_with_error) # Format the list of failed volumes
                    self.failed_volumes_label.configure(text=f"Failed Volumes: {failed_vol_str}", text_color="#cc3300") # Update the failed volumes label

                elif self.num_success >= 1 and self.num_error >= 1: # If some volumes were successful and some failed
                    self.status_label.configure(text="Backup Partially Complete!", text_color="#cc6d00") # Update the status label
                    failed_vol_str = self.vol_report( self.vol_with_error) # Format the list of failed volumes
                    self.failed_volumes_label.configure(text= f"Failed Volumes: {failed_vol_str}", text_color="#cc3300") # Update the failed volumes label
                    success_vol_str = self.vol_report(self.vol_with_success) # Format the list of successful volumes
                    self.volumes_backed_up_label.configure(text=f"Volumes Backed Up: {success_vol_str}", text_color="#1fa59d") # Update the backed up volumes label
                self.close_button.configure(text="Close") # Update the text of the close button when the backup is complete

            else:
                self.after(15000, self.monitor_status) # Schedule the monitor_status function to run again after 15000 milliseconds (15 seconds)

    def on_close(self):
        """
        Handles the event when the close button is clicked or the window is closed.
        It unfades the main application window and navigates the user back to the home screen.
        """
        self.unfade_app() # Call the unfade_app method to make the main application window visible again
        self.master.master.route_home() # Call the route_home method of the main application to navigate to the home screen
        self.destroy() # Destroy the JobStatus popup window