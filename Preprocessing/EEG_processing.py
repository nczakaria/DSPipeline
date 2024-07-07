import mne
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import skew, kurtosis
from scipy.signal import welch
from scipy.integrate import simps
import os

def extract_time_domain_features(window):
    # Calculate mean, variance, skewness, and kurtosis of the window
    features = {}
    features['mean'] = np.mean(window)
    features['variance'] = np.var(window)
    features['skewness'] = skew(window)
    features['kurtosis'] = kurtosis(window)
    
    return features

def extract_frequency_domain_features(window, sampling_freq, window_size):
    # Compute Power Spectral Density (PSD) using Welch's method
    freqs, psd = welch(window, fs=sampling_freq, nperseg=window_size)
    freqs_res = freqs[1] - freqs[0]  # Frequency resolution
    total_power = simps(psd, dx=freqs_res)  # Total power in the signal
    features = {}

    # Define frequency bands
    bands = {
        "delta": (0.5, 4),
        "theta": (4, 8),
        "alpha": (8, 12),
        "beta": (12, 30),
        "gamma": (30, 100)
    }
    
    for band, (low, high) in bands.items():
        # Find the indices of the frequencies within the band
        idx = np.logical_and(freqs >= low, freqs <= high)
        # Calculate absolute band power using Simpson's rule for numerical integration
        abs_power = simps(psd[idx], dx=freqs_res)
        # Calculate relative band power
        rel_power = abs_power / total_power
        features[f"{band} abs power"] = abs_power
        features[f"{band} rel power"] = rel_power
        
    # Calculate the ratio of delta power to beta power as an index of slow-wave sleep quality
    features['slow-wave sleep quality'] = features['delta abs power'] / features['beta abs power'] if features['beta abs power'] != 0 else np.NaN
    
    return features

def moving_window(data, window_duration, time_step, sampling_freq):
    # List to store feature dictionaries for each window
    features_list = []
    
    window_size = int(sampling_freq * window_duration)  # Number of samples per window
    step_size = int(sampling_freq * time_step)  # Number of samples to step
    
    for i in range(0, len(data) - window_size + 1, step_size):
        window = data['amplitude'][i:min(i + window_size, len(data['time']))]
        
        features = {}
        features['Window_index'] = i // step_size + 1  # Index of the window
        # Extract and add time-domain features to the features dictionary
        features.update(extract_time_domain_features(window))
        # Extract and add frequency-domain features to the features dictionary
        features.update(extract_frequency_domain_features(window, sampling_freq, window_size))
        # Append the features dictionary to the list
        features_list.append(features)
    
    return pd.DataFrame(features_list)

def save_features(channel_name, save_path, df):
            csv_path = os.path.join(save_path, f"{channel_name}.csv")
            df.to_csv(csv_path, index=False)
            
    
def extract_eeg_features(file_path, save_path, config):
    #Load the EDF file
    raw = mne.io.read_raw_edf(file_path, preload=True)
    
    channel_names = raw.info['ch_names']
        
    for channel_name in channel_names:
        if 'eeg' in channel_name.lower():
            channel = raw.copy().pick_channels([channel_name])
            #Select the channel
            data, times = channel[:]
            sampling_freq = raw.info['sfreq']
            
            #Create a DataFrame for the channel data
            channel_df = pd.DataFrame({'time': times, 'amplitude': data[0]})
            feature_df = moving_window(channel_df, config.window_duration, config.time_step, sampling_freq)
            
            # Save the csv
            save_features(channel_name, save_path, feature_df)
    
            
            



