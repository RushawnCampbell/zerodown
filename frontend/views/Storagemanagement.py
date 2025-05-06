import customtkinter as gui
import datetime
import math
from frontend.views.Listview import Listview
from frontend.Utility.CommonMethods import CommonMethods

class Storagemanagement(Listview):
    def __init__(self, master):
        super().__init__(master, title="Storage Management")
        self.sample_storage_data = CommonMethods.get_objects("storagenodes", self.master.app_name, self.master.windows_user)
        self.no_data_message = "No storages registered as yet"
        self.register_button = None
        self._check_and_populate(self.sample_storage_data)

    def _check_and_populate(self, data):
        super()._check_and_populate(data)
        if not self.sample_storage_data:
            self.register_button = gui.CTkButton(self.item_frame, text="Register storage", command=lambda viewclassname='storageregistration' : self.master.show_view(viewclassname))
            self.register_button.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")
            self.item_frame.grid_rowconfigure(1, weight=1)

    def _populate_item_frame(self, data_list):
        # Clear existing widgets in the frame
        for widget in self.item_frame.winfo_children():
            widget.destroy()

        if data_list:
            gui.CTkLabel(self.item_frame, text="Storage Name", font=gui.CTkFont(weight="bold"), anchor="w").grid(row=0, column=0, padx=10, pady=(10, 10), sticky="ew")
            gui.CTkLabel(self.item_frame, text="Date Registered", font=gui.CTkFont(weight="bold"), anchor="w").grid(row=0, column=1, padx=10, pady=(10, 10), sticky="ew")
            # Removed the "Track UpTime" label

            start_index = self.current_page * self.records_per_view
            end_index = min((self.current_page + 1) * self.records_per_view, len(data_list))
            current_data = data_list[start_index:end_index]

            for i, data in enumerate(current_data):
                row_num = i + 1
                gui.CTkLabel(self.item_frame, text=data["storage_name"], anchor="w").grid(row=row_num, column=0, padx=10, pady=10, sticky="ew")
                gui.CTkLabel(self.item_frame, text=data["storage_reg_date"], anchor="w").grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")
                # Removed the track_switch
                remove_button = gui.CTkButton(self.item_frame, text="Remove", fg_color="#cc3300", width=80, command=lambda name=data["storage_id"]: self._remove_storage(name))
                remove_button.grid(row=row_num, column=2, padx=5, pady=7, sticky="ew")
                more_button = gui.CTkButton(self.item_frame, text="More", width=80, command=lambda name=data["storage_id"]: self._show_more_info(name))
                more_button.grid(row=row_num, column=3, padx=5, pady=7, sticky="ew")

            self.item_frame.grid_columnconfigure(0, weight=2)
            self.item_frame.grid_columnconfigure(1, weight=1)
            self.item_frame.grid_columnconfigure(2, weight=0) # For the Remove button
            self.item_frame.grid_columnconfigure(3, weight=0) # For the More button
            # Removed the grid_columnconfigure for the switch column
        else:
            pass

    def _remove_storage(self, storage_name):
        print(f"Removing storage: {storage_name}")
        # Implement actual removal logic

    def _show_more_info(self, storage_name):
        print(f"Showing more info for: {storage_name}")
        # Implement showing more info

    def _toggle_tracking(self, storage_name):
        print(f"Tracking toggled for: {storage_name}")
        # Implement tracking toggle logic