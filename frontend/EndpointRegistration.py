import customtkinter as gui
from frontend.components.Popup import Popup
from PIL import Image

class EndpointRegistration(gui.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.master = master
        self._configure_ui()
        self._create_widgets()
        self._layout_widgets()

    def _configure_ui(self):
        """Configures the UI appearance and grid layout."""
        self.configure(fg_color="#2B2B2B")
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _create_widgets(self):
        """Creates and initializes all UI widgets."""
        self.view_title_frame = gui.CTkFrame(self)
        self.view_title = gui.CTkLabel(
            self.view_title_frame,
            text="Register Endpoint",
            font=gui.CTkFont(size=20, weight="bold"),
            wraplength=700,
            justify="center",
        )

        self.form_body = gui.CTkFrame(self)
        self.form_body.configure(fg_color="#000000")
        self.form_body.grid_columnconfigure(0, weight=1)
        for i in range(4):
            self.form_body.grid_rowconfigure(i * 2, weight=1)
            self.form_body.grid_rowconfigure(i * 2 + 1, weight=1)

        self.step1_label = gui.CTkLabel(self.form_body, text="STEP 1: DEFINE ENDPOINT", font=gui.CTkFont(size=15, weight="bold"), anchor="w")
        self.step1_entry_frame = gui.CTkFrame(self.form_body)
        self.step1_entry_frame.grid_columnconfigure(1, weight=2)  # Give more weight to entries
        self.step1_entry_frame.grid_columnconfigure(3, weight=2)  # Give more weight to entries
        self.step1_entry_frame.configure(fg_color="#000000")

        self.step1_label1 = gui.CTkLabel(self.step1_entry_frame, text="Name", anchor="w")
        self.step1_entry1 = gui.CTkEntry(self.step1_entry_frame, text_color="#000000", border_color="#FFFFFF")
        self.step1_entry1.configure(fg_color="#FFFFFF")
        self.step1_label2 = gui.CTkLabel(self.step1_entry_frame, text="IP Address", anchor="w")
        self.step1_entry2 = gui.CTkEntry(self.step1_entry_frame, text_color="#000000", border_color="#FFFFFF")
        self.step1_entry2.configure(fg_color="#FFFFFF")

        self.step2_label = gui.CTkLabel(self.form_body, text="STEP 2: DOWNLOAD ENDPOINT INSTALLER",font=gui.CTkFont(size=15, weight="bold"), anchor="w")
        self.download_image = Image.open("./frontend/assets/icons/download.png")
        self.ctk_download_image = gui.CTkImage(light_image=self.download_image, dark_image=self.download_image, size=(25, 25))
        self.step2_button = gui.CTkButton(self.form_body,image=self.ctk_download_image, text="Download Endpoint Installer", command=self.download_installer)

        self.step3_label = gui.CTkLabel(self.form_body, text="STEP 3: TEST CONNECTION", font=gui.CTkFont(size=15, weight="bold"), anchor="w")
        self.test_image = Image.open("./frontend/assets/icons/Test.png")
        self.ctk_test_image = gui.CTkImage(light_image=self.test_image, dark_image=self.test_image, size=(25, 25))
        self.step3_button = gui.CTkButton(self.form_body,image=self.ctk_test_image, text="Test Connection (Not Yet Tested)")

        self.step4_label = gui.CTkLabel(self.form_body, text="STEP 4: COMPLETE REGISTRATION", font=gui.CTkFont(size=15, weight="bold"), anchor="w")
        self.complete_reg_image = Image.open("./frontend/assets/icons/check-list.png")
        self.ctk_complete_reg_image = gui.CTkImage(light_image=self.complete_reg_image, dark_image=self.complete_reg_image, size=(25, 25))
        self.step4_button = gui.CTkButton(self.form_body, image=self.ctk_complete_reg_image, text="Complete Registration")
        self.step4_button.configure(fg_color="#1fa59d")

    def _layout_widgets(self):
        """Arranges the widgets within the grid layout."""
        self.view_title_frame.grid(row=0, column=0, padx=40, pady=20, sticky="nsew")
        self.view_title.pack(pady=(0, 0), padx=0, fill="x")

        self.form_body.grid(row=1, column=0, padx=100, pady=(0, 20), sticky="nsew")

        self.step1_label.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.step1_entry_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.step1_label1.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.step1_entry1.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.step1_label2.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self.step1_entry2.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.step2_label.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.step2_button.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.step3_label.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.step3_button.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.step4_label.grid(row=6, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.step4_button.grid(row=7, column=0, padx=20, pady=(0, 10), sticky="ew")

    def download_installer(self):
        download_pup = Popup(self, "Downloading Endpoint Installer")