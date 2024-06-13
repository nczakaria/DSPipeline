import os
from Signal_Processing import ECG_processing as ecg
from Signal_Processing import EEG_processing as eeg
from Audio import Audio_processing as audio
from pathlib import Path



class DataLoader:
    # Initialize the DataLoader with the data path and save path
    def __init__(self, data_path, save_path, config):
        # Set the data path and save path
        self.data_path = data_path
        self.save_path = save_path
        self.config = config
        
        
        # Supported file formats
        self.audio_format = ['.mp3', '.ogg', '.flac', '.m4a']
        self.eeg_format = ['.edf']
        self.ecg_format = ['.dat']
        
    
    # Get the file type from the file path
    def get_file_type(self, file_path):
        _, file_extension = os.path.splitext(file_path)
        return file_extension.lower()
    
    
    # Load the data from the data path
    def load_data(self):
        # Get the list of files in the data path
        files = os.listdir(self.data_path)
        # Load the data from each file
        for file in files:
            # Get the file and check if it is supported
            file_path = os.path.join(self.data_path, file)
            file_type = self.get_file_type(file_path)
            
            # Load the data based on the file type
            if file_type in self.eeg_format:
                self.load_eeg(file_path)
            
            elif file_type in self.ecg_format:
                self.load_ecg(file_path)
            
            elif file_type in self.audio_format:
                self.load_audio(file_path)
            
            else:
                print(f"Unsupported file format: {file_type}")
    
    # Load the EEG features from the file
    def load_eeg(self, file_path):
        # Create EEG_Save_path and load EEG features
        eeg_folder_path = Path(self.save_path) / "EEG"
        eeg_folder_path.mkdir(parents=True, exist_ok=True)
        
        eeg.extract_eeg_features(file_path, eeg_folder_path, self.config)
    
    # Load the ECG features from the file
    def load_ecg(self, file_path):
        # Create ECG_Save_path and load ECG features
        ecg_folder_path = Path(self.save_path) / "ECG"
        ecg_folder_path.mkdir(parents=True, exist_ok=True)
        
        ecg.extract_ecg_features(file_path, ecg_folder_path, self.config)
    
    # Load the Audio features from the file
    def load_audio(self, file_path):
        # Create Audio_Save_path and load Audio features
        audio_folder_path = Path(self.save_path) / "Audio"
        audio_folder_path.mkdir(parents=True, exist_ok=True)
        
        audio.extract_audio_features(file_path, audio_folder_path, self.config)

