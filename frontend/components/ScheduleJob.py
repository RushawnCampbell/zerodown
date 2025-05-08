import customtkinter as gui
import tkinter as tk
import tkinter.ttk as ttk
import requests
from tkcalendar import Calendar
from datetime import datetime
from frontend.components.Popup import Popup
import tkinter.messagebox

class ScheduleJob(Popup):
    def __init__(self, master, title, job_name):
        super().__init__(master, title)
        self.title(title)
        self.job_name=job_name
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(7, weight=1) # Increased row configure to accommodate the new row

        self.date_label = gui.CTkLabel(self, text="Pick Backup Start Date:", text_color="#2b2b2b")
        self.date_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month
        self.current_day = now.day
        self.calendar = Calendar(
            self,
            selectmode='day',
            date_pattern='yyyy-mm-dd',
            mindate=datetime(self.current_year, self.current_month, self.current_day),
            showweeknumbers=False,
            command=self.date_selected  # Call date_selected on date selection
        )
        self.calendar.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="nsew")

        self.time_label = gui.CTkLabel(self, text="Pick Backup Time:", text_color="#2b2b2b")
        self.time_label.grid(row=0, column=1, padx=20, pady=(20, 5), sticky="w")

        self.time_picker_frame = gui.CTkFrame(self)
        self.time_picker_frame.grid(row=1, column=1, padx=20, pady=(5, 10), sticky="nsew")

        self.hour_label = gui.CTkLabel(self.time_picker_frame, text="Hour:")
        self.hour_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.hour_options_12hr = []
        for i in range(24):
            if i == 0:
                self.hour_options_12hr.append(f"{12:02d} AM")
            elif 1 <= i < 12:
                self.hour_options_12hr.append(f"{i:02d} AM")
            elif i == 12:
                self.hour_options_12hr.append(f"{12:02d} PM")
            else:
                self.hour_options_12hr.append(f"{i - 12:02d} PM")
        self.hour_combobox = gui.CTkComboBox(self.time_picker_frame, values=self.hour_options_12hr, width=100, command=self.time_selected)
        current_hour_12hr_ampm = datetime.now().strftime("%I %p").lstrip("0")
        self.hour_combobox.set(current_hour_12hr_ampm)
        self.hour_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.minute_label = gui.CTkLabel(self.time_picker_frame, text="Minute:")
        self.minute_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.minute_options = [f"{i:02d}" for i in range(60)]
        self.minute_combobox = gui.CTkComboBox(self.time_picker_frame, values=self.minute_options, width=100, command=self.time_selected)
        self.minute_combobox.set(f"{datetime.now().minute:02d}")
        self.minute_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Restructured Frequency and Copies row
        self.frequency_label = gui.CTkLabel(self, text="Frequency:", text_color="#2b2b2b")
        self.frequency_label.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")

        self.frequency_combobox = ttk.Combobox(self, values=["One Time", "Daily", "Weekly", "Monthly"], width=15)
        self.frequency_combobox.set("One Time")
        self.frequency_combobox.grid(row=2, column=0, padx=(150, 20), pady=(10, 5), sticky="w") # Placed in column 0, adjusted padx
        self.frequency_combobox.bind("<<ComboboxSelected>>", self.frequency_generator)

        self.num_copies_label = gui.CTkLabel(self, text="No. of Copies to Keep:", text_color="#2b2b2b")
        self.num_copies_label.grid(row=2, column=1, padx=(20, 0), pady=(10, 5), sticky="w")

        self.num_copies_entry = gui.CTkEntry(self, width=90, fg_color="#FFFFFF", text_color="#2b2b2b", border_width=1, height=10, border_color="#000000", corner_radius=0)
        self.num_copies_entry.grid(row=2, column=1, padx=(170, 20), pady=(10, 5), sticky="w") # Placed in column 1, adjusted padx

        self.weekly_buttons_frame = None
        self.selected_day = tk.StringVar()
        self.selected_day.set(None)

        self.schedule_button = gui.CTkButton(self, text="Schedule Job", command=self.configure_schedule)
        self.schedule_button.grid(row=6, column=0, columnspan=2, pady=20, sticky="s") # Moved down due to new row

        self.after(1000, self.set_window_position, 700, 350)

    def date_selected(self, date_str):
        print(f"Selected date: {date_str}")
        self.update_selected_datetime()

    def time_selected(self, event=None):
        self.update_selected_datetime()

    def update_selected_datetime(self):
        selected_date_str = self.calendar.get_date()
        selected_hour_12hr_ampm = self.hour_combobox.get()
        selected_minute = self.minute_combobox.get()

        try:
            hour_str, ampm = selected_hour_12hr_ampm.split()
            hour = int(hour_str)
            if ampm == "PM" and hour != 12:
                hour += 12
            elif ampm == "AM" and hour == 12:
                hour = 0
            selected_hour_24hr = f"{hour:02d}"

            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
            self.master.sch_datetime = datetime(selected_date.year, selected_date.month, selected_date.day,
                                                int(selected_hour_24hr), int(selected_minute)).strftime("%Y-%m-%d %H:%M:%S")
            print(f"Selected date and time: {self.master.sch_datetime}")
        except ValueError:
            print("Invalid date or time format while updating.")
            self.master.sch_datetime = None

    def print_selected_day(self):
        selected_day = self.selected_day.get()
        print(f"Selected day: {selected_day}")

    def frequency_generator(self, event=None):
        selected_frequency = self.frequency_combobox.get()
        print(f"Selected frequency: {selected_frequency}")

        if self.weekly_buttons_frame:
            self.weekly_buttons_frame.destroy()
            self.weekly_buttons_frame = None
            self.schedule_button.grid(row=6, column=0, columnspan=2, pady=20, sticky="s") # Moved down

        if selected_frequency == "Weekly":
            self.weekly_buttons_frame = gui.CTkFrame(self)
            self.weekly_buttons_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(5, 5), sticky="ew")

            days_map = {"Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday", "Thu": "Thursday", "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday"}
            for i, day_abbr in enumerate(days_map.keys()):
                day_radio = gui.CTkRadioButton(
                    self.weekly_buttons_frame,
                    text=day_abbr,
                    value=day_abbr,
                    variable=self.selected_day,
                    command=self.print_selected_day
                )
                day_radio.pack(side="left", padx=0)

            self.schedule_button.grid(row=5, column=0, columnspan=2, pady=(10, 20), sticky="s") # Moved down

            self.update_idletasks()
            self.update()

    def configure_schedule(self):
        selected_frequency = self.frequency_combobox.get()
        selected_day_abbr = self.selected_day.get()
        num_archive_copies = self.num_copies_entry.get()

        if selected_frequency == "Weekly":
            if selected_day_abbr == "None" or selected_day_abbr == "":
                tk.messagebox.showerror("No Selected Day", "You Must Select A Day For Your Weekly Backups")
                return None  # Indicate failure

            selected_date_str = self.calendar.get_date()
            try:
                selected_date_obj = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
                selected_weekday = selected_date_obj.strftime("%A")  # Get full weekday name

                days_map = {"Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday", "Thu": "Thursday", "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday"}
                selected_full_day = days_map.get(selected_day_abbr)

                if selected_full_day and selected_weekday != selected_full_day:
                    tk.messagebox.showerror(
                        "Day Mismatch",
                        f"The selected day ({selected_full_day}) does not match the date on the calendar ({selected_weekday}). Please adjust either the selected day or the calendar date."
                    )
                    return None
            except ValueError:
                tk.messagebox.showerror("Calendar Error", "Could not parse the calendar date.")
                return None


        if not num_archive_copies.isdigit() or int(num_archive_copies) < 1:
            tk.messagebox.showerror("Value Error", "The number of copies to keep is invalid. You must enter a number greater than 0, please try again.")
            return None
        else:
            self.master.num_copies_to_keep = int(num_archive_copies)
        # Get the final datetime object
        schedule_datetime = None
        if self.master.sch_datetime is None:
            default_date_str = self.calendar.get_date()
            default_hour_12hr_ampm = self.hour_combobox.get()
            default_minute = self.minute_combobox.get()
            try:
                hour_str, ampm = default_hour_12hr_ampm.split()
                hour = int(hour_str)
                if ampm == "PM" and hour != 12:
                    hour += 12
                elif ampm == "AM" and hour == 12:
                    hour = 0
                default_hour_24hr = f"{hour:02d}"
                default_date = datetime.strptime(default_date_str, "%Y-%m-%d").date()
                schedule_datetime = datetime(default_date.year, default_date.month, default_date.day,
                                                    int(default_hour_24hr), int(default_minute))
            except ValueError:
                tk.messagebox.showerror("Error", "Could not determine default date and time.")
                return -1
        else:
            schedule_datetime = datetime.strptime(self.master.sch_datetime, "%Y-%m-%d %H:%M:%S")

        # time in 12-hour AM/PM format
        formatted_time = schedule_datetime.strftime("%I:%M %p")

        confirmation_message = f"Would You to Continue With The Following Schedule?\n\nStart Date: {schedule_datetime.strftime('%Y-%m-%d')}\nStart Time: {formatted_time}\nFrequency: {selected_frequency}"
        if selected_frequency == "Weekly" and selected_day_abbr:
            days_map = {"Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday", "Thu": "Thursday", "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday"}
            confirmation_message += f"\nDay: {days_map.get(selected_day_abbr)}s"
        if num_archive_copies:
            confirmation_message += f"\nNumber of Archive Copies: {num_archive_copies}"

        if tk.messagebox.askyesno("Schedule Confirmation", confirmation_message):
            self.master.sch_frequency = selected_frequency
            if selected_frequency == "Weekly":
                self.master.sch_day = selected_day_abbr
            self.master.sch_datetime = schedule_datetime.strftime("%Y-%m-%d %H:%M:%S") # Store as string for consistency
            try:
                self.master.num_archive_copies = int(num_archive_copies) if num_archive_copies else None
            except ValueError:
                tk.messagebox.showerror("Input Error", "Number of archive copies must be an integer.")
                return -1

            self.create_schedule()
            return 0  # Indicate success
        else:
            return -1  # Indicate cancellation

    def create_schedule(self):
        resource_url= f"http://127.0.0.1:8080/zeroapi/v1/backup/schedule"
        zauth_token = self.master.master.retrieve_auth_token()
        zeroheaders = {"Authorization": f"Bearer {zauth_token}", "Content-Type": "application/json"}
        schedule_data = {
            "endpoint_name": self.master.endpoint_name,
            "backup_targets": self.master.selected_endpoint_info,
            "backup_destinations": self.master.selected_storage_info,
            "name": self.job_name,
            "sch_datetime": self.master.sch_datetime,
            "sch_frequency": self.master.sch_frequency,
            "sch_day": self.master.sch_day,
            "num_archive_copies" : self.master.num_archive_copies
        }
        if hasattr(self.master, 'num_archive_copies') and self.master.num_archive_copies is not None:
            schedule_data["num_archive_copies"] = self.master.num_archive_copies

        try:
            response = requests.post(resource_url, stream=True, headers=zeroheaders, json=schedule_data)
            response.raise_for_status()
            response_code = response.status_code
            response= response.json()
            schedule_status = response['response']

            if response_code == 200:
                self.unfade_app()
                self.destroy()
                tk.messagebox.showinfo("Scheduling Successful", f"{self.job_name} Was Scheduled Successfully")
            else:
                tk.messagebox.showerror("Scheduling Error", f"{schedule_status}. Contact ZeroDown Support If The Error Persists.")

        except requests.exceptions.RequestException as e:
            tk.messagebox.showerror("Scheduling Error", f"An Unexpected Error Occurred. Please Try Again or Contact ZeroDown Support If The Error Persists.")