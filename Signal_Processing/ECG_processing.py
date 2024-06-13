import wfdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks, savgol_filter
import os

# Define the bandpass filter function
def bandpass_filter(signal, lowcut, highcut, fs, order=4):
    nyquist_freq = 0.5 * fs
    low = lowcut / nyquist_freq
    high = highcut / nyquist_freq
    b, a = butter(order, [low, high], btype='band')
    # Check signal length
    padlen = 3 * max(len(b), len(a))  # filtfilt pad length
    # Raise error if the singal not is long enough
    if signal.shape[0] <= padlen:
        raise ValueError(f"The length of the input vector x must be greater than padlen, which is {padlen}.")
    y = filtfilt(b, a, signal, axis=0)  # Apply along the time axis
    return y

# Remove the noise of the signal by smoothing it
def smoothing_singal(signal_data, fs, lowcut, highcut):
    for i in range(signal_data.shape[1]):
        signal_data[:, i] = bandpass_filter(signal=signal_data[:, i], lowcut=lowcut, highcut=highcut, fs=fs)

    # Apply Savitzky-Golay filter to each channel
    smoothed_signals = np.zeros_like(signal_data)
    window_length = 51  # Ensure this is an odd number and less than the length of the data

    for i in range(signal_data.shape[1]):
        # Ensure the window length is appropriate, if not raise an error
        if window_length > len(signal_data[:, i]):
            raise ValueError(f"Window length {window_length} is too large for the signal length {len(signal_data[:, i])}.")
        smoothed_signals[:, i] = savgol_filter(signal_data[:, i], window_length=window_length, polyorder=3)
    
    return smoothed_signals
    


def find_q_s_points(r_peaks, ecg_signal, sampling_freq, range=0.08):
    # Set up the range to find q_s points
    window_range = int(sampling_freq * range)
    q_points = []
    s_points = []
    
    # loop through all r peaks
    for peak in r_peaks:
        # Set up the start and end point for q and s intervals and extract the local min for each intervals
        q_start_point = max(0, peak - window_range)
        s_end_point = min(peak + window_range, len(ecg_signal))

        q_point = q_start_point + np.argmin(ecg_signal[q_start_point:peak])
        q_points.append(q_point)

        s_point = peak + np.argmin(ecg_signal[peak:s_end_point])
        s_points.append(s_point)

    return q_points, s_points


def find_p_t_points(r_peaks, q_points, s_points, ecg_signal, sampling_freq, p_range=0.4, t_range=0.5):
    p_points = []
    t_points = []
    # Find the deriviatve of the signal
    first_derivative = np.diff(ecg_signal)
    
    for i in range(len(r_peaks)):
        # Pass the first point 
        if i == 0:
            continue
        
        # Define search window for P wave before the Q wave
        p_start_point = max(0, r_peaks[i] - int(p_range * sampling_freq))
        p_end_point = q_points[i]

        # Define search window for T wave after the S wave
        t_start_point = s_points[i]
        t_end_point = min(len(ecg_signal), r_peaks[i] + int(t_range * sampling_freq))

        # Find the P point as the maximum within the defined window
        p_peak_x = None
        p_peak_y = -np.inf
        for x in range(p_start_point, p_end_point):
            if 0 < x < len(first_derivative) and first_derivative[x - 1] > 0 and first_derivative[x] < 0:
                if ecg_signal[x] > p_peak_y:
                    p_peak_x = x
                    p_peak_y = ecg_signal[x]
        if p_peak_x is not None:
            p_points.append(p_peak_x)

        # Find the T point as the maximum within the defined window
        t_peak_x = None
        t_peak_y = -np.inf
        for x in range(t_start_point, t_end_point):
            if 0 < x < len(first_derivative) and first_derivative[x - 1] > 0 and first_derivative[x] < 0:
                if ecg_signal[x] > t_peak_y:
                    t_peak_x = x
                    t_peak_y = ecg_signal[x]
        if t_peak_x is not None:
            t_points.append(t_peak_x)

    return p_points, t_points


def find_onset_offset_points(ecg_signal, peaks, sampling_freq, is_onset, search_range):
    # Set up the deriviat  ve
    first_derivative = np.diff(ecg_signal)
    crit_points = []
    for peak in peaks:
        # If finding the onset point
        if is_onset:
            start = max(0, peak - int(search_range * sampling_freq))
            end = peak
            # Loop through the points and find the critical points
            for j in range(end - 2, start, -1):
                if j - 2 < 0:  # Prevent index out of bounnds
                    break
                if all(first_derivative[j - k] > 0 for k in range(1, 3)) and all(first_derivative[j + k] < 0 for k in range(1, 3)):
                    crit_points.append(j)
                    break
        else:
            start = peak
            end = min(len(ecg_signal) - 1, peak + int(search_range * sampling_freq))\
            # Loop through the points and find the critical points
            for j in range(start + 2, end):
                if j + 2 >= len(first_derivative):  # Ensure we do not go out of bounds
                    break
                if all(first_derivative[j - k] < 0 for k in range(1, 3)) and all(first_derivative[j + k] > 0 for k in range(1, 3)):
                    crit_points.append(j)
                    break
    return crit_points

def plot_signal(ecg_signal, fs, r_peaks, q_points, s_points, p_points, t_points, p_onsets, q_onsets, s_offsets, t_offsets):
    # Convert lists to NumPy arrays
    q_points = np.array(q_points)
    s_points = np.array(s_points)
    p_points = np.array(p_points)
    t_points = np.array(t_points)

    p_onsets = np.array(p_onsets)
    q_onsets = np.array(q_onsets)
    s_offsets = np.array(s_offsets)
    t_offsets = np.array(t_offsets)
    # Calculate the time vector in seconds
    time_vector = np.arange(ecg_signal.size) / fs

    # Convert to integer indices
    r_peaks_within_range = r_peaks[r_peaks < 6000]
    q_points_within_range = q_points[q_points < 6000]
    s_points_within_range = s_points[s_points < 6000]
    p_points_within_range = p_points[p_points < 6000]
    t_points_within_range = t_points[t_points < 6000]

    p_onsets_within_range = p_onsets[p_onsets < 6000]
    q_onsets_within_range = q_onsets[q_onsets < 6000]
    s_offsets_within_range = s_offsets[s_offsets < 6000]
    t_offsets_within_range = t_offsets[t_offsets < 6000]


    # Get y-values for the detected points
    r_peaks_y = ecg_signal[r_peaks_within_range]
    q_points_y = ecg_signal[q_points_within_range]
    s_points_y = ecg_signal[s_points_within_range]
    p_points_y = ecg_signal[p_points_within_range]
    t_points_y = ecg_signal[t_points_within_range]

    p_onsets_y = ecg_signal[p_onsets_within_range]
    q_onsets_y = ecg_signal[q_onsets_within_range]
    s_offsets_y = ecg_signal[s_offsets_within_range]
    t_offsets_y = ecg_signal[t_offsets_within_range]

    # Plot the detected points
    plt.figure(figsize=(10, 6))
    plt.plot(time_vector[:6000], ecg_signal[:6000], label='ECG Signal')
    plt.scatter(r_peaks_within_range / fs, r_peaks_y, color='r', label='R-peaks', zorder=2)
    plt.scatter(q_points_within_range / fs, q_points_y, color='b', label='Q-points', zorder=2)
    plt.scatter(s_points_within_range / fs, s_points_y, color='g', label='S-points', zorder=2)
    plt.scatter(p_points_within_range / fs, p_points_y, color='m', label='P-points', zorder=2)
    plt.scatter(t_points_within_range / fs, t_points_y, color='c', label='T-points', zorder=2)

    plt.scatter(p_onsets_within_range / fs, p_onsets_y, color='y', label='P-onsets', zorder=2)
    plt.scatter(q_onsets_within_range / fs, q_onsets_y, color='k', label='Q-onsets', zorder=2)
    plt.scatter(s_offsets_within_range / fs, s_offsets_y, color='orange', label='S-offsets', zorder=2)
    plt.scatter(t_offsets_within_range / fs, t_offsets_y, color='purple', label='T-offsets', zorder=2)

    plt.title('ECG Signal')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.show()



def extract_time_features(ecg_signal, sampling_freq):
    # Get all the peak points
    r_peaks, _ = find_peaks(ecg_signal, distance=int(sampling_freq / 2.5), height=np.mean(ecg_signal) + 2*np.std(ecg_signal))
    q_points, s_points = find_q_s_points(r_peaks, ecg_signal, sampling_freq)
    p_points, t_points = find_p_t_points(r_peaks, q_points, s_points, ecg_signal, sampling_freq)

    # Find the on/offsets pounts and convert lists to NumPy arrays
    p_onsets = np.array(find_onset_offset_points(ecg_signal, p_points, sampling_freq, is_onset=True, search_range=0.1))
    q_onsets = np.array(find_onset_offset_points(ecg_signal, q_points, sampling_freq, is_onset=True, search_range=0.1))
    t_offsets = np.array(find_onset_offset_points(ecg_signal, t_points, sampling_freq, is_onset=False, search_range=0.2))
    s_offsets = np.array(find_onset_offset_points(ecg_signal, s_points, sampling_freq, is_onset=False, search_range=0.2))

    # Ensure arrays have matching lengths
    min_length = min(len(p_onsets), len(q_onsets))
    p_onsets = p_onsets[:min_length]
    q_onsets = q_onsets[:min_length]

    # Find all the features needed
    p_wave_durations = (q_onsets - p_onsets) / sampling_freq

    min_length = min(len(q_onsets), len(s_offsets))
    q_onsets = q_onsets[:min_length]
    s_offsets = s_offsets[:min_length]

    qrs_durations = (s_offsets - q_onsets) / sampling_freq

    min_length = min(len(s_offsets), len(t_offsets))
    s_offsets = s_offsets[:min_length]
    t_offsets = t_offsets[:min_length]

    t_wave_durations = (t_offsets - s_offsets) / sampling_freq

    min_length = min(len(p_onsets), len(q_onsets))
    pr_intervals = (q_onsets[:min_length] - p_onsets[:min_length]) / sampling_freq

    min_length = min(len(q_onsets), len(t_offsets))
    qt_intervals = (t_offsets[:min_length] - q_onsets[:min_length]) / sampling_freq

    features = []
    
    # Save the features in the dictionary
    for cycle in range(0, len(r_peaks) - 1):
        feature = {}
        rr_interval = r_peaks[cycle + 1] - r_peaks[cycle]
        bpm = 60.0 / (rr_interval / sampling_freq)
        feature['RR_interval'] = rr_interval / sampling_freq
        feature['BPM'] = bpm
        feature['P_Wave_duration'] = p_wave_durations[cycle] if cycle < len(p_wave_durations) else np.nan
        feature['QRS_duration'] = qrs_durations[cycle] if cycle < len(qrs_durations) else np.nan
        feature['T_Wave_duration'] = t_wave_durations[cycle] if cycle < len(t_wave_durations) else np.nan
        feature['PR_interval'] = pr_intervals[cycle] if cycle < len(pr_intervals) else np.nan
        feature['QT_interval'] = qt_intervals[cycle] if cycle < len(qt_intervals) else np.nan
        features.append(feature)

    return features, r_peaks, q_points, s_points, p_points, t_points, p_onsets, q_onsets, s_offsets, t_offsets


def read_signal(file_path):
    # Extract the base name without the directory path and extension
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    # Construct the header file path
    header_file = f"{os.path.join(os.path.dirname(file_path), base_name)}.hea"
    print(base_name, header_file)
    # Check if the header file exists
    if not os.path.exists(header_file):
        raise FileNotFoundError(f"No header file found for {file_path}")
    
    # Read the header and record
    record = wfdb.rdrecord(os.path.join(os.path.dirname(file_path), base_name))
    signal = record.p_signal
    fs = record.fs
    
    return fs, signal



def save_features(channel_name, save_path , df):
    csv_path = os.path.join(save_path, f"{channel_name}.csv")
    df.to_csv(csv_path, index=False)


def extract_ecg_features(file_path, save_path, config):
        fs, signal = read_signal(file_path)
        smoothed_signal = smoothing_singal(signal, fs, config.ecg_low_cutoff, config.ecg_high_cutoff)
        for i in range(smoothed_signal.shape[1]):
            # Extract features and detect peaks
            channel_signal = smoothed_signal[:, i]
            features, r_peaks, q_points, s_points, p_points, t_points, p_onsets, q_onsets, s_offsets, t_offsets = extract_time_features(channel_signal, fs)
            df_features = pd.DataFrame(features)
            #plot_signal(channel_signal, r_peaks, q_points, s_points, p_points, t_points, p_onsets, q_onsets, s_offsets, t_offsets)
            save_features(i+1, save_path, df_features)
        
        
        

