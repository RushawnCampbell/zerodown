import customtkinter as gui, traceback, json, requests, tkinter as tk
from PIL import Image
from frontend.components.RemoteExplorer import RemoteExplorer
from frontend.components.JobStatus import JobStatus
from frontend.components.ScheduleJob import ScheduleJob
import datetime
import math

class Endpointmanagement(gui.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("ZeroDown: Endpoint Management")
        self.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.records_per_view = 10 
        self.current_page = 0
        self.num_pages = 0
        self.max_visible_buttons = 10

        self.grid_rowconfigure(0, weight=0) # For the endpoint management label
        self.grid_rowconfigure(1, weight=1) # For the endpoint frame
        self.grid_rowconfigure(2, weight=0) # For the pagination frame
        self.grid_columnconfigure(0, weight=1)

        # Endpoint Management Label
        self.endpoint_label = gui.CTkLabel(self, text="Endpoint Management", font=gui.CTkFont(size=16, weight="bold"), anchor="w")
        self.endpoint_label.grid(row=0, column=0, padx=20, pady=(20, 2), sticky="ew")

        self.endpoint_frame = gui.CTkScrollableFrame(self)
        self.endpoint_frame.grid(row=1, column=0, padx=20, pady=(2, 10), sticky="nsew")
        self.endpoint_frame.configure(fg_color="#202020")

        self.pagination_frame = gui.CTkFrame(self)
        self.pagination_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.pagination_frame.configure(fg_color="transparent") # Make it transparent
        self.pagination_frame.grid_columnconfigure(0, weight=1) # Center content

        self.sample_endpoint_data = [
            {"Endpoint Name": f"Server-{chr(65+i)}", "Date Registered": datetime.datetime.now().strftime("%Y-%m-%d")} for i in range(105)
        ] # Initialize with more sample data for pagination testing

        self.endpoint_no_data_label = None
        self.endpoint_register_button = None
        self.prev_button = None
        self.next_button = None
        self.page_buttons = []

        self._check_and_populate_endpoints()

    def _check_and_populate_endpoints(self):
        if not self.sample_endpoint_data:
            self.endpoint_no_data_label = gui.CTkLabel(self.endpoint_frame, text="No Endpoints registered as yet")
            self.endpoint_no_data_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="ew")
            self.endpoint_register_button = gui.CTkButton(self.endpoint_frame, text="Register Endpoint", command=lambda viewclassname='endpointregistration' : self.master.show_view(viewclassname))
            self.endpoint_register_button.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")
            self.endpoint_frame.grid_rowconfigure(0, weight=1) # Center vertically
            self.endpoint_frame.grid_rowconfigure(1, weight=1) # Center vertically
            self.endpoint_frame.grid_columnconfigure(0, weight=1) # Center horizontally
            # Hide pagination frame if no data
            self.pagination_frame.grid_forget()
        else:
            self.num_pages = math.ceil(len(self.sample_endpoint_data) / self.records_per_view)
            self._populate_endpoint_frame(self.sample_endpoint_data)
            self._create_pagination_buttons()

    def _populate_endpoint_frame(self, data_list):
        # Clear existing widgets in the frame
        for widget in self.endpoint_frame.winfo_children():
            widget.destroy()

        start_index = self.current_page * self.records_per_view
        end_index = min((self.current_page + 1) * self.records_per_view, len(data_list))
        current_data = data_list[start_index:end_index]

        if current_data:
            gui.CTkLabel(self.endpoint_frame, text="Endpoint Name", font=gui.CTkFont(weight="bold"), anchor="w").grid(row=0, column=0, padx=10, pady=(10, 10), sticky="ew")
            gui.CTkLabel(self.endpoint_frame, text="Date Registered", font=gui.CTkFont(weight="bold"), anchor="w").grid(row=0, column=1, padx=10, pady=(10, 10), sticky="ew")
            gui.CTkLabel(self.endpoint_frame, text="Track UpTime", font=gui.CTkFont(weight="bold"), anchor="w").grid(row=0, column=2, padx=10, pady=(10, 10), sticky="ew") # Left aligned
            gui.CTkLabel(self.endpoint_frame, text="", font=gui.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=(10, 10), sticky="ew") # For Remove button
            gui.CTkLabel(self.endpoint_frame, text="", font=gui.CTkFont(weight="bold")).grid(row=0, column=4, padx=5, pady=(10, 10), sticky="ew") # For More button


            for i, data in enumerate(current_data):
                row_num = i + 1
                gui.CTkLabel(self.endpoint_frame, text=data["Endpoint Name"], anchor="w").grid(row=row_num, column=0, padx=10, pady=10, sticky="ew") # Increased pady
                gui.CTkLabel(self.endpoint_frame, text=data["Date Registered"], anchor="w").grid(row=row_num, column=1, padx=10, pady=10, sticky="ew") # Increased pady
                track_switch = gui.CTkSwitch(self.endpoint_frame, text="", onvalue="on", offvalue="off", command=lambda name=data["Endpoint Name"]: self._toggle_tracking(name))
                track_switch.grid(row=row_num, column=2, padx=10, pady=7, sticky="ew") # Increased pady
                remove_button = gui.CTkButton(self.endpoint_frame, text="Remove", fg_color="#cc3300", width=80, command=lambda name=data["Endpoint Name"]: self._remove_endpoint(name))
                remove_button.grid(row=row_num, column=3, padx=5, pady=7, sticky="ew") # Increased pady
                more_button = gui.CTkButton(self.endpoint_frame, text="More", width=80, command=lambda name=data["Endpoint Name"]: self._show_more_info(name))
                more_button.grid(row=row_num, column=4, padx=5, pady=7, sticky="ew") # Increased pady

            self.endpoint_frame.grid_columnconfigure(0, weight=2) # Endpoint Name
            self.endpoint_frame.grid_columnconfigure(1, weight=1) # Date Registered
            self.endpoint_frame.grid_columnconfigure(2, weight=0) # Track
            self.endpoint_frame.grid_columnconfigure(3, weight=0) # Remove
            self.endpoint_frame.grid_columnconfigure(4, weight=0) # More
        else:
            pass

    def _create_pagination_buttons(self):
        # Clear existing pagination buttons
        if self.prev_button:
            self.prev_button.destroy()
            self.prev_button = None
        for button in self.page_buttons:
            button.destroy()
        self.page_buttons = []
        if self.next_button:
            self.next_button.destroy()
            self.next_button = None

        if self.num_pages > 1:
            self.pagination_frame.grid() # Ensure pagination frame is visible
            inner_frame = gui.CTkFrame(self.pagination_frame, fg_color="transparent")
            inner_frame.grid(row=0, column=0, padx=0, pady=0, sticky="ew")

            self.prev_button = gui.CTkButton(inner_frame, text="Prev", width=60, command=self._prev_page)
            self.prev_button.pack(side="left", padx=(0, 5), pady=5)
            if self.current_page == 0:
                self.prev_button.configure(state="disabled")

            visible_page_numbers = []
            if self.num_pages <= self.max_visible_buttons:
                visible_page_numbers = range(self.num_pages)
            else:
                start = max(0, self.current_page - self.max_visible_buttons // 2)
                end = min(self.num_pages, start + self.max_visible_buttons)
                if end - start < self.max_visible_buttons and end < self.num_pages:
                    start = max(0, self.num_pages - self.max_visible_buttons)
                visible_page_numbers = range(start, end)

                if 0 not in visible_page_numbers and self.num_pages > self.max_visible_buttons:
                    button = gui.CTkButton(inner_frame, text="1", width=40, command=lambda page=0: self._change_page(page))
                    if 0 == self.current_page:
                        button.configure(fg_color="#1fa59d")
                    else:
                        button.configure(fg_color="#1B1B1B")
                    button.pack(side="left", padx=5, pady=5)
                    if visible_page_numbers[0] > 1:
                        label = gui.CTkLabel(inner_frame, text="...")
                        label.pack(side="left", padx=5, pady=5)


            for i in visible_page_numbers:
                button = gui.CTkButton(inner_frame, text=str(i + 1), width=40,
                                       command=lambda page=i: self._change_page(page))
                if i == self.current_page:
                    button.configure(fg_color="#1fa59d")
                else:
                    button.configure(fg_color="#1B1B1B")
                button.pack(side="left", padx=5, pady=5)
                self.page_buttons.append(button)

            if visible_page_numbers[-1] < self.num_pages - 1:
                label = gui.CTkLabel(inner_frame, text="...")
                label.pack(side="left", padx=5, pady=5)
                button = gui.CTkButton(inner_frame, text=str(self.num_pages), width=40, command=lambda page=self.num_pages - 1: self._change_page(page))
                if self.num_pages - 1 == self.current_page:
                    button.configure(fg_color="#1fa59d")
                else:
                    button.configure(fg_color="#1B1B1B")
                button.pack(side="left", padx=5, pady=5)


            self.next_button = gui.CTkButton(inner_frame, text="Next", width=60, command=self._next_page)
            self.next_button.pack(side="left", padx=(5, 0), pady=5)
            if self.current_page == self.num_pages - 1:
                self.next_button.configure(state="disabled")
        else:
            # Hide pagination frame if not needed
            self.pagination_frame.grid_forget()

    def _change_page(self, page_number):
        self.current_page = page_number
        self._populate_endpoint_frame(self.sample_endpoint_data)
        self._create_pagination_buttons() # Re-render buttons to update active state

    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._populate_endpoint_frame(self.sample_endpoint_data)
            self._create_pagination_buttons()

    def _next_page(self):
        if self.current_page < self.num_pages - 1:
            self.current_page += 1
            self._populate_endpoint_frame(self.sample_endpoint_data)
            self._create_pagination_buttons()

    def _remove_endpoint(self, endpoint_name):
        print(f"Removing endpoint: {endpoint_name}")
        # In a real application, you would update the self.sample_endpoint_data and then call
        # self._check_and_populate_endpoints() to refresh the view.

    def _show_more_info(self, endpoint_name):
        print(f"Showing more info for: {endpoint_name}")

    def _toggle_tracking(self, endpoint_name):
        print(f"Tracking toggled for: {endpoint_name}")