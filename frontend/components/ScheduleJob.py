import customtkinter as gui
import tkinter as tk
import tkinter.ttk as ttk  # Import the ttk module
from tkcalendar import Calendar
from datetime import datetime
from frontend.components.Popup import Popup


class ScheduleJob(Popup):
    def __init__(self, master, title):
        super().__init__(master, title)
        self.title(title)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(5, weight=1)  # Adjusted row weight to accommodate the new row

        # Get the current date
        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month
        self.current_day = now.day

        # Calendar Widget (Date Picker) (Row 0)
        self.calendar = Calendar(
            self,
            selectmode='day',
            date_pattern='yyyy-mm-dd',
            mindate=datetime(self.current_year, self.current_month, self.current_day),
            showweeknumbers=False  # Hide the leftmost column with week numbers
        )
        self.calendar.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew") # Adjusted pady

        # Time Picker Frame (Row 0)
        self.time_picker_frame = gui.CTkFrame(self)
        self.time_picker_frame.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="nsew") # Adjusted pady

        self.hour_label = gui.CTkLabel(self.time_picker_frame, text="Hour:")
        self.hour_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.hour_options = [f"{i:02d}" for i in range(24)]
        self.hour_combobox = gui.CTkComboBox(self.time_picker_frame, values=self.hour_options, width=80)
        self.hour_combobox.set("00")  # Default value
        self.hour_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.minute_label = gui.CTkLabel(self.time_picker_frame, text="Minute:")
        self.minute_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.minute_options = [f"{i:02d}" for i in range(60)]
        self.minute_combobox = gui.CTkComboBox(self.time_picker_frame, values=self.minute_options, width=80)
        self.minute_combobox.set("00")  # Default value
        self.minute_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Frequency Label and Dropdown (Row 1)
        self.frequency_label = gui.CTkLabel(self, text="Frequency:")
        self.frequency_label.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w") # Adjusted pady

        self.frequency_options = ["One Time", "Daily", "Weekly", "Monthly"]
        self.frequency_combobox = ttk.Combobox(self, values=self.frequency_options, width=15) # Use ttk.Combobox
        self.frequency_combobox.set("One Time")  # Default value
        self.frequency_combobox.grid(row=1, column=1, padx=20, pady=(10, 5), sticky="e") # Adjusted pady
        self.frequency_combobox.bind("<<ComboboxSelected>>", self.frequency_generator) # Bind to <<ComboboxSelected>>

        self.weekly_buttons_frame = None  # To hold the weekly buttons
        self.selected_day = tk.StringVar()
        self.selected_day.set(None)

        # Schedule Job Button (Row 4 initially, might move down)
        self.schedule_button = gui.CTkButton(self, text="Schedule Job", command=self.schedule_job)
        self.schedule_button.grid(row=4, column=0, columnspan=2, pady=20, sticky="s") # Adjusted row

        self.after(1000, self.center_window) # Using a dedicated method for centering

    def center_window(self):
        width = 600
        height = 500
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def frequency_generator(self, event=None): # Now receives the event object
        print("Frequency Generator called")
        selected_frequency = self.frequency_combobox.get()
        print(f"Selected frequency: {selected_frequency}")

        # Destroy any existing weekly buttons frame
        if self.weekly_buttons_frame:
            self.weekly_buttons_frame.destroy()
            self.weekly_buttons_frame = None
            self.schedule_button.grid(row=4, column=0, columnspan=2, pady=20, sticky="s") # Reset schedule button position

        if selected_frequency == "Weekly":
            self.weekly_buttons_frame = gui.CTkFrame(self)
            self.weekly_buttons_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(5, 20), sticky="ew") # Row 2
            print("Weekly frame created and gridded")

            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            for i, day in enumerate(days):
                day_radio = gui.CTkRadioButton(self.weekly_buttons_frame, text=day, value=day, variable=self.selected_day)
                day_radio.pack(side="left", padx=5)

            self.schedule_button.grid(row=5, column=0, columnspan=2, pady=20, sticky="s") # Move schedule button down

            self.update_idletasks()
            self.update()

    def schedule_job(self):
        selected_date_str = self.calendar.get_date()
        selected_hour = self.hour_combobox.get()
        selected_minute = self.minute_combobox.get()
        selected_frequency = self.frequency_combobox.get()

        print(f"Scheduling frequency: {selected_frequency}")
        if selected_frequency == "Weekly" and self.weekly_buttons_frame:
            selected_day = self.selected_day.get()
            print(f"Selected day: {selected_day}")

        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
            scheduled_time = datetime(selected_date.year, selected_date.month, selected_date.day,
                                        int(selected_hour), int(selected_minute))
            print(f"Scheduling job for: {scheduled_time}")  # your scheduling logic here
            self.destroy()  # Close the toplevel window
        except ValueError:
            print("Invalid date or time format")