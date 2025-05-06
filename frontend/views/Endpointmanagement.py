import customtkinter as gui
import datetime
import math
from frontend.views.Listview import Listview
from frontend.Utility.CommonMethods import CommonMethods
from frontend.components.SingleEndpoint import SingleEndpoint
from tkinter import messagebox

class Endpointmanagement(Listview):
    def __init__(self, master):
        super().__init__(master, title="Endpoint Management")
        self.sample_endpoint_data = CommonMethods.get_objects("endpoints", self.master.app_name, self.master.windows_user)
        self.no_data_message = "No Endpoints registered as yet"
        self.register_button = None
        self._check_and_populate(self.sample_endpoint_data)

    def _check_and_populate(self, data):
        super()._check_and_populate(data)
        if not self.sample_endpoint_data:
            self.register_button = gui.CTkButton(self.item_frame, text="Register Endpoint", command=lambda viewclassname='endpointregistration' : self.master.show_view(viewclassname))
            self.register_button.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")
            self.item_frame.grid_rowconfigure(1, weight=1)

    def _populate_item_frame(self, data_list):
        # Clear existing widgets in the frame
        for widget in self.item_frame.winfo_children():
            widget.destroy()

        if data_list:
            gui.CTkLabel(self.item_frame, text="Endpoint Name", font=gui.CTkFont(weight="bold"), anchor="w").grid(row=0, column=0, padx=10, pady=(10, 10), sticky="ew")
            gui.CTkLabel(self.item_frame, text="Date Registered", font=gui.CTkFont(weight="bold"), anchor="w").grid(row=0, column=1, padx=10, pady=(10, 10), sticky="ew")
            gui.CTkLabel(self.item_frame, text="Track UpTime", font=gui.CTkFont(weight="bold"), anchor="w").grid(row=0, column=2, padx=10, pady=(10, 10), sticky="ew")
            gui.CTkLabel(self.item_frame, text="", font=gui.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=(10, 10), sticky="ew")
            gui.CTkLabel(self.item_frame, text="", font=gui.CTkFont(weight="bold")).grid(row=0, column=4, padx=5, pady=(10, 10), sticky="ew")

            start_index = self.current_page * self.records_per_view
            end_index = min((self.current_page + 1) * self.records_per_view, len(data_list))
            current_data = data_list[start_index:end_index]

            for i, data in enumerate(current_data):
                row_num = i + 1
                gui.CTkLabel(self.item_frame, text=data["endpoint_name"], anchor="w").grid(row=row_num, column=0, padx=10, pady=10, sticky="ew")
                gui.CTkLabel(self.item_frame, text=data["endpoint_reg_date"], anchor="w").grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")
                track_switch = gui.CTkSwitch(self.item_frame, text="", onvalue="on", offvalue="off", command=lambda name=data["endpoint_id"]: self._toggle_tracking(name))
                track_switch.grid(row=row_num, column=2, padx=10, pady=7, sticky="ew")
                remove_button = gui.CTkButton(self.item_frame, text="Remove", fg_color="#cc3300", width=80, command=lambda name=data["endpoint_name"], id=data["endpoint_id"]: self._confirm_remove_endpoint(name, id))
                remove_button.grid(row=row_num, column=3, padx=5, pady=7, sticky="ew")
                more_button = gui.CTkButton(self.item_frame, text="More", width=80, command=lambda name=data["endpoint_name"], id=data["endpoint_id"]: self._show_more_info(name, id))
                more_button.grid(row=row_num, column=4, padx=5, pady=7, sticky="ew")

            self.item_frame.grid_columnconfigure(0, weight=2)
            self.item_frame.grid_columnconfigure(1, weight=1)
            self.item_frame.grid_columnconfigure(2, weight=0)
            self.item_frame.grid_columnconfigure(3, weight=0)
            self.item_frame.grid_columnconfigure(4, weight=0)
        else:
            pass

    def _confirm_remove_endpoint(self, endpoint_name, endpoint_id):
        confirmation = messagebox.askyesno(
            "Confirm Endpoint Removal",
            f"{endpoint_name.title()} will be unpaired from its associated Storage Nodes and you will need to register it again. Would you like to continue?"
        )
        if confirmation:
            print("yes is selected")
            self._remove_endpoint(endpoint_name,endpoint_id)
        else:
            pass

    def _remove_endpoint(self, endpoint_name, endpoint_id):
        print(f"Removing endpoint: {endpoint_name}")
        # Implement actual removal logic

    def _show_more_info(self, endpoint_name,endpoint_id):
        SingleEndpoint(self, f"{endpoint_name} Details", endpoint_id)

    def _toggle_tracking(self, endpoint_name):
        print(f"Tracking toggled for: {endpoint_name}")
        # Implement tracking toggle logic