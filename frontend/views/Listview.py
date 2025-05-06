import customtkinter as gui
import math

class Listview(gui.CTkFrame):
    def __init__(self, master, title):
        super().__init__(master)
        self.master = master
        self.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.records_per_view = 10
        self.current_page = 0
        self.num_pages = 0
        self.max_visible_buttons = 10
        self.data_list = []  # To be populated by child classes
        self.no_data_message = "No items available." # Can be overridden

        self.grid_rowconfigure(0, weight=0) # Title
        self.grid_rowconfigure(1, weight=1) # Item frame
        self.grid_rowconfigure(2, weight=0) # Pagination frame
        self.grid_columnconfigure(0, weight=1)

        self.title_label = gui.CTkLabel(self, text=title, font=gui.CTkFont(size=16, weight="bold"), anchor="w")
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 2), sticky="ew")

        self.item_frame = gui.CTkScrollableFrame(self)
        self.item_frame.grid(row=1, column=0, padx=20, pady=(2, 10), sticky="nsew")
        self.item_frame.configure(fg_color="#202020")

        self.pagination_frame = gui.CTkFrame(self)
        self.pagination_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.pagination_frame.configure(fg_color="transparent")
        self.pagination_frame.grid_columnconfigure(0, weight=1)

        self.no_data_label = None
        self.prev_button = None
        self.next_button = None
        self.page_buttons = []

    def _check_and_populate(self, data):
        self.data_list = data
        if not self.data_list:
            self._show_no_data_message()
            self.pagination_frame.grid_forget()
        else:
            self.num_pages = math.ceil(len(self.data_list) / self.records_per_view)
            self._populate_item_frame(self.data_list)
            self._create_pagination_buttons()

    def _show_no_data_message(self):
        self.no_data_label = gui.CTkLabel(self.item_frame, text=self.no_data_message)
        self.no_data_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="ew")
        self.item_frame.grid_rowconfigure(0, weight=1)
        self.item_frame.grid_columnconfigure(0, weight=1)

    def _populate_item_frame(self, data_list):
        # To be implemented by child classes to display specific item details
        raise NotImplementedError

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
            self.pagination_frame.grid()
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
            self.pagination_frame.grid_forget()

    def _change_page(self, page_number):
        self.current_page = page_number
        self._populate_item_frame(self.data_list)
        self._create_pagination_buttons()

    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._populate_item_frame(self.data_list)
            self._create_pagination_buttons()

    def _next_page(self):
        if self.current_page < self.num_pages - 1:
            self.current_page += 1
            self._populate_item_frame(self.data_list)
            self._create_pagination_buttons()