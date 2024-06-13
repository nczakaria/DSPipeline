import tkinter as tk
from tkinter import filedialog
from config import Config
from data_loader import DataLoader


# Data Loader UI class
class DataLoaderUI:
    # Initialize the UI with the main window
    def __init__(self, master):
        self.master = master
        master.title("Data Loader")

        font = ("Helvetica", 12)

        # Data Folder Selection
        self.data_label = tk.Label(
            master, text="Select the folder where your data is stored:", font=font
        )
        self.data_label.pack(pady=5)

        self.data_button = tk.Button(
            master,
            text="Select Data Folder",
            command=self.select_data_folder,
            font=font,
        )
        self.data_button.pack(pady=5)

        # Save Folder Selection
        self.save_label = tk.Label(
            master,
            text="Select the folder where processed data features will be stored:",
            font=font,
        )
        self.save_label.pack(pady=5)

        self.save_button = tk.Button(
            master,
            text="Select Save Folder",
            command=self.select_save_folder,
            font=font,
        )
        self.save_button.pack(pady=5)

        # Data Type Label
        self.param_label = tk.Label(master, text="Data Type:", font=font)
        self.param_label.pack(pady=10)

        # Data Type Checkboxes
        self.eeg_var = tk.BooleanVar()
        self.ecg_var = tk.BooleanVar()
        self.audio_var = tk.BooleanVar()

        self.eeg_check = tk.Checkbutton(
            master,
            text="EEG",
            variable=self.eeg_var,
            command=self.toggle_sections,
            font=font,
        )
        self.eeg_check.pack()
        self.ecg_check = tk.Checkbutton(
            master,
            text="ECG",
            variable=self.ecg_var,
            command=self.toggle_sections,
            font=font,
        )
        self.ecg_check.pack()
        self.audio_check = tk.Checkbutton(
            master,
            text="Audio",
            variable=self.audio_var,
            command=self.toggle_sections,
            font=font,
        )
        self.audio_check.pack()

        # EEG Parameters Frame
        self.eeg_frame = tk.LabelFrame(
            master, text="EEG Parameters", padx=10, pady=10, font=font
        )
        self.eeg_frame.pack(padx=10, pady=10)

        self.window_duration_label = tk.Label(
            self.eeg_frame, text="Window Duration (seconds):", font=font
        )
        self.window_duration_label.grid(row=0, column=0, sticky="e")
        self.window_duration_entry = tk.Entry(self.eeg_frame, font=font)
        self.window_duration_entry.grid(row=0, column=1)

        self.time_step_label = tk.Label(
            self.eeg_frame, text="Time Step (seconds):", font=font
        )
        self.time_step_label.grid(row=1, column=0, sticky="e")
        self.time_step_entry = tk.Entry(self.eeg_frame, font=font)
        self.time_step_entry.grid(row=1, column=1)

        # ECG Parameters Frame
        self.ecg_frame = tk.LabelFrame(
            master, text="ECG Parameters", padx=10, pady=10, font=font
        )
        self.ecg_frame.pack(padx=10, pady=10)

        self.ecg_low_cut_off_label = tk.Label(
            self.ecg_frame, text="ECG Low Cutoff Frequency (Hz):", font=font
        )
        self.ecg_low_cut_off_label.grid(row=0, column=0, sticky="e")
        self.ecg_low_cut_off_entry = tk.Entry(self.ecg_frame, font=font)
        self.ecg_low_cut_off_entry.grid(row=0, column=1)

        self.ecg_high_cut_off_label = tk.Label(
            self.ecg_frame, text="ECG High Cutoff Frequency (Hz):", font=font
        )
        self.ecg_high_cut_off_label.grid(row=1, column=0, sticky="e")
        self.ecg_high_cut_off_entry = tk.Entry(self.ecg_frame, font=font)
        self.ecg_high_cut_off_entry.grid(row=1, column=1)

        # Audio Parameters Frame
        self.audio_frame = tk.LabelFrame(
            master, text="Audio Parameters", padx=10, pady=10, font=font
        )
        self.audio_frame.pack(padx=10, pady=10)

        self.audio_low_cutoff_label = tk.Label(
            self.audio_frame, text="Audio Low Cutoff Frequency (Hz):", font=font
        )
        self.audio_low_cutoff_label.grid(row=0, column=0, sticky="e")
        self.audio_low_cutoff_entry = tk.Entry(self.audio_frame, font=font)
        self.audio_low_cutoff_entry.grid(row=0, column=1)

        self.audio_high_cutoff_label = tk.Label(
            self.audio_frame, text="Audio High Cutoff Frequency (Hz):", font=font
        )
        self.audio_high_cutoff_label.grid(row=1, column=0, sticky="e")
        self.audio_high_cutoff_entry = tk.Entry(self.audio_frame, font=font)
        self.audio_high_cutoff_entry.grid(row=1, column=1)

        self.sr_label = tk.Label(
            self.audio_frame, text="Sampling Rate (Hz):", font=font
        )
        self.sr_label.grid(row=2, column=0, sticky="e")
        self.sr_entry = tk.Entry(self.audio_frame, font=font)
        self.sr_entry.grid(row=2, column=1)

        self.hop_length_label = tk.Label(
            self.audio_frame, text="Hop Length (samples):", font=font
        )
        self.hop_length_label.grid(row=3, column=0, sticky="e")
        self.hop_length_entry = tk.Entry(self.audio_frame, font=font)
        self.hop_length_entry.grid(row=3, column=1)

        # Load Data Button
        self.load_button = tk.Button(
            master,
            text="Load Data",
            command=self.load_data,
            state=tk.DISABLED,
            font=font,
        )
        self.load_button.pack(pady=10)

        self.data_folder_path = ""
        self.save_folder_path = ""

        # Initialize the parameter sections as disabled
        self.toggle_sections()

    # Toggle the parameter sections based on the data type selection
    def toggle_sections(self):
        # Enable or disable the EEG, ECG, and Audio parameter sections based on the selection
        if self.eeg_var.get():
            self.enable_frame(self.eeg_frame)
        else:
            self.disable_frame(self.eeg_frame)

        if self.ecg_var.get():
            self.enable_frame(self.ecg_frame)
        else:
            self.disable_frame(self.ecg_frame)

        if self.audio_var.get():
            self.enable_frame(self.audio_frame)
        else:
            self.disable_frame(self.audio_frame)

    # Enable all the widgets in a frame
    def enable_frame(self, frame):
        for child in frame.winfo_children():
            child.configure(state="normal")

    # Disable all the widgets in a frame
    def disable_frame(self, frame):
        for child in frame.winfo_children():
            child.configure(state="disabled")

    # Select the data folder
    def select_data_folder(self):
        self.data_folder_path = filedialog.askdirectory()
        if self.data_folder_path:
            self.show_custom_message(
                "Selected Folder", f"Data folder selected: {self.data_folder_path}"
            )
            self.enable_load_button()
        else:
            self.show_custom_message(
                "No Folder Selected", "Please select a folder to load data from."
            )

    # Select the save folder
    def select_save_folder(self):
        self.save_folder_path = filedialog.askdirectory()
        if self.save_folder_path:
            self.show_custom_message(
                "Selected Folder", f"Save folder selected: {self.save_folder_path}"
            )
            self.enable_load_button()
        else:
            self.show_custom_message(
                "No Folder Selected",
                "Please select a folder to save processed data to.",
            )

    # Enable the load button if both data and save folders are selected
    def enable_load_button(self):
        if self.data_folder_path and self.save_folder_path:
            self.load_button.config(state=tk.NORMAL)


    def load_data(self):
        try:
        # Initialize parameters with default values or None
            window_duration = time_step = ecg_low_cut_off = ecg_high_cut_off = (
                audio_low_cutoff
            ) = audio_high_cutoff = sr = hop_length = None

            # Parse EEG parameters if EEG is selected
            if self.eeg_var.get():
                window_duration = float(self.window_duration_entry.get())
                time_step = float(self.time_step_entry.get())

            # Parse ECG parameters if ECG is selected
            if self.ecg_var.get():
                ecg_low_cut_off = float(self.ecg_low_cut_off_entry.get())
                ecg_high_cut_off = float(self.ecg_high_cut_off_entry.get())

            # Parse Audio parameters if Audio is selected
            if self.audio_var.get():
                audio_low_cutoff = float(self.audio_low_cutoff_entry.get())
                audio_high_cutoff = float(self.audio_high_cutoff_entry.get())
                sr = int(self.sr_entry.get())
                hop_length = int(self.hop_length_entry.get())

            config = Config(
            window_duration,
            time_step,
            ecg_low_cut_off,
            ecg_high_cut_off,
            audio_low_cutoff,
            audio_high_cutoff,
            sr,
            hop_length,
            )
        except ValueError:
            self.show_custom_message(
            "Invalid Input", "Please enter valid numbers for all parameters."
            )
            return

        if self.data_folder_path and self.save_folder_path:
            dataloader = DataLoader(self.data_folder_path, self.save_folder_path, config)
            dataloader.load_data()
            self.show_custom_message("Data Loading", "Data loading completed.")
        else:
            self.show_custom_message(
                "Folder Selection Incomplete", "Please select both data and save folders."
            )

    def show_custom_message(self, title, message):
        CustomMessageBox(self.master, title, message)


# Custom message box class
class CustomMessageBox:
    def __init__(self, master, title, message):
        self.master = master
        self.title = title
        self.message = message
        self.create_message_box()

    # Create the message box window
    def create_message_box(self):
        # Create a new top-level window
        self.top = tk.Toplevel(self.master)
        self.top.title(self.title)
        window_width = 300
        window_height = 150
        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        # Set the window size and position
        self.top.geometry(
            f"{window_width}x{window_height}+{position_right}+{position_top}"
        )
        self.label = tk.Label(self.top, text=self.message, wraplength=280)
        self.label.pack(pady=20)
        self.ok_button = tk.Button(self.top, text="OK", command=self.top.destroy)
        self.ok_button.pack(pady=10)
