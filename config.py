class  Config:
    def __init__(self, window_duration, time_step, ecg_low_cutoff, ecg_high_cutoff, audio_low_cutoff, audio_high_cutoff, sr, hop_length):
        
        # EEG Features
        self.window_duration = window_duration
        self.time_step = time_step
        
        # ECG Features
        self.ecg_low_cutoff = ecg_low_cutoff
        self.ecg_high_cutoff = ecg_high_cutoff
        
        #  Audio Parameters
        self.audio_low_cutoff = audio_low_cutoff
        self.audio_high_cutoff = audio_high_cutoff
        self.n_fft = 2048
        self.sr = sr
        self.hop_length = hop_length
        self.n_mels = 256
        self.cmap = "coolwarm"
        self.window_type = "hann"
        self.fmin = 20
        self.fmax = 8000