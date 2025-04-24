import customtkinter as gui
import tkinter as tk
import tkinter.ttk as ttk
from tkcalendar import Calendar
from datetime import datetime
from frontend.components.Popup import Popup


class ScheduleJob(Popup):
    def __init__(self, master, title):
        super().__init__(master, title)
        self.title(title)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(6, weight=1)

        self.selected_datetime = None

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
        self.minute_combobox = gui.CTkComboBox(self.time_picker_frame, values=self.minute_options, width=80, command=self.time_selected)
        self.minute_combobox.set(f"{datetime.now().minute:02d}")
        self.minute_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.frequency_label = gui.CTkLabel(self, text="Frequency:", text_color="#2b2b2b")
        self.frequency_label.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")

        self.frequency_options = ["One Time", "Daily", "Weekly", "Monthly"]
        self.frequency_combobox = ttk.Combobox(self, values=self.frequency_options, width=15)
        self.frequency_combobox.set("One Time")
        self.frequency_combobox.grid(row=2, column=1, padx=20, pady=(10, 5), sticky="e")
        self.frequency_combobox.bind("<<ComboboxSelected>>", self.frequency_generator)

        self.weekly_buttons_frame = None
        self.selected_day = tk.StringVar()
        self.selected_day.set(None)

        self.schedule_button = gui.CTkButton(self, text="Schedule Job", command=self.schedule_job)
        self.schedule_button.grid(row=5, column=0, columnspan=2, pady=20, sticky="s")

        self.after(1000, self.set_window_position, 700, 350)

    def center_window(self):
        width = 600
        height = 500
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

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
            self.selected_datetime = datetime(selected_date.year, selected_date.month, selected_date.day,
                                              int(selected_hour_24hr), int(selected_minute))
            print(f"Selected date and time: {self.selected_datetime}")
        except ValueError:
            print("Invalid date or time format while updating.")
            self.selected_datetime = None

    def print_selected_day(self):
        selected_day = self.selected_day.get()
        print(f"Selected day: {selected_day}")

    def frequency_generator(self, event=None):
        selected_frequency = self.frequency_combobox.get()
        print(f"Selected frequency: {selected_frequency}")

        if self.weekly_buttons_frame:
            self.weekly_buttons_frame.destroy()
            self.weekly_buttons_frame = None
            self.schedule_button.grid(row=5, column=0, columnspan=2, pady=20, sticky="s")

        if selected_frequency == "Weekly":
            self.weekly_buttons_frame = gui.CTkFrame(self)
            self.weekly_buttons_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(5, 5), sticky="ew")

            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            for i, day in enumerate(days):
                day_radio = gui.CTkRadioButton(
                    self.weekly_buttons_frame,
                    text=day,
                    value=day,
                    variable=self.selected_day,
                    command=self.print_selected_day
                )
                day_radio.pack(side="left", padx=0)

            self.schedule_button.grid(row=4, column=0, columnspan=2, pady=(10, 20), sticky="s")

            self.update_idletasks()
            self.update()

    def schedule_job(self):
            self.master.sch_datetime = self.selected_datetime
            self.master.sch_frequency = self.frequency_combobox.get()
            if  self.master.sch_frequency == "Weekly":
                self.master.sch_day = self.selected_day.get()
                print("SELECTED DAY IS", self.master.sch_day)
                if self.master.sch_day == "None" or self.master.sch_day == "":
                    tk.messagebox.showerror("No Selected Day", f"You Must Select A Day For Your Weekly Backups")
            else:
                self.master.backup_now()
                self.destroy()