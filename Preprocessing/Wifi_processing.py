import pandas as pd
import numpy as np
import os
import csv
import re
from pathlib import Path
from datetime import datetime, timedelta

class Config:
    def __init__(self, window_duration, time_step, ecg_low_cutoff, ecg_high_cutoff, audio_low_cutoff, audio_high_cutoff, sr, hop_length, wifi_sample_rate, wifi_window_size):
        
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
        
        # Wifi parameters
        self.wifi_sample_rate = wifi_sample_rate
        self.wifi_window_size = wifi_window_size
        
def create_hash_key(path):
    if os.path.exists(path):
        df = pd.read_csv(path)
        code = df["Code"]
        hashes = df["MACHashed"]

        hash_key = {}
        for code, hash_ in zip(code, hashes):
            hash_key[hash_] = code

        return hash_key
    else:
        print(f"File not found: {path}")
        return None

def clean_df(df):
    df = df.dropna(axis=1, how="all")
    print(df.head())
    return df

def get_comma_indices(line):
    return [match.start() for match in re.finditer(",", line)]

def process_csv(csv_path):
    cleaned_rows = []
    with open(csv_path, mode="r", newline="") as file:
        reader = csv.reader(file)
        header = next(reader)
        cleaned_rows.append(header)

        for row in reader:
            line = ",".join(row)  # Join the row into a single string
            comma_indices = get_comma_indices(line)
            clenaed_line = line[: comma_indices[-3]]
            cleaned_row = clenaed_line.split(",")

            cleaned_rows.append(cleaned_row)

    with open(csv_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(cleaned_rows)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2) * np.sin(dlat / 2) + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) * np.sin(dlon / 2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

def extract_features(df, hash_key, config):
    window_size = config.wifi_window_size
    print(df.dtypes)
    
    df.loc[:, "Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")
    df.loc[:, "hour"] = df.loc[:, "LastSeen"].dt.hour
    df.loc[:, "day_oclf_week"] = df.loc[:, "LastSeen"].dt.dayofweek
    
    df['Previous_LastSeen'] = df.gropby('Client_Mac')['LastSeen'].shft(1)
    
    df['time_since_last_seen'] = (df['LastSeen'] - df['Previous_LastSeen']).dt.total_seconds()
    df.drop(columns=['Previous_LastSeen'], inplace=True)
    df['time_since_last_seen'] = df['time_since_last_seen'].fillna('')
    
    
    df.loc[:, "rssi_avg"] = df.groupby("Client_Mac")["Max_RSSI"].rolling(window=window_size).mean().reset_index(0, drop=True)
    
    df.loc[:, "rssi_std"] = df.groupby("Client_Mac")["Max_RSSI"].rolling(window=window_size).std().reset_index(0, drop=True)

    meassure_power = -30  # Measure power value at 1 meter
    path_loss_exponent = 2  # 2 for indoor environment normally

    df["proximity"] = 10 ** ((meassure_power - df["Max_RSSI"]) / (10 * path_loss_exponent))
    
    unique_device_counts = []

    for i in range(len(df)):
        if i < window_size:
            preceding_rows = df.iloc[:i+1]
        else:
            preceding_rows = df.iloc[i-window_size+1:i+1]
    
        unique_device_count = len(preceding_rows['Client_Mac'].unique())
        unique_device_counts.append(unique_device_count)

    df['unique_device_count'] = unique_device_counts
    
    df.loc[:, 'lat_shifted'] = df.groupby('Client_Mac')['Lat'].shift()
    df.loc[:, 'long_shifted'] = df.groupby('Client_Mac')['Long'].shift()
    df.loc[:, 'distance'] = haversine(df['Lat'], df['Long'], df['lat_shifted'], df['long_shifted'])
    df.loc[:, "time_diff"] = df.groupby("Client_Mac")["LastSeen"].diff().dt.total_seconds()
    df.loc[:, 'speed'] = df['distance'] / df['time_diff']
    
    df.drop(['lat_shifted', 'long_shifted', 'time_diff'], axis=1, inplace=True)
    
    return df

def save_features(df_list, save_path, sample_rate):
    start_time, end_time = df_list.pop().split("_")
    end_time = end_time.replace('.csv', '')
    
    start_time = datetime.fromtimestamp(int(start_time) / 1000)
    end_time = datetime.fromtimestamp(int(end_time) / 1000)
    
    start_time_str = start_time.strftime("%Y-%m-%d_%H-%M-%S")
    end_time_str = end_time.strftime("%Y-%m-%d_%H-%M-%S")
    
    dir_path = Path(save_path) / f"{start_time_str}_{end_time_str}"
    os.makedirs(dir_path, exist_ok=True)
    
    sample_rate = int(sample_rate.split("min")[0])
    
    for i in range(len(df_list)):
        start_stamp = start_time + timedelta(minutes=sample_rate * i)
        end_stamp = min(end_time, start_stamp + timedelta(minutes=sample_rate))
        start_stamp_str = start_stamp.strftime("%Y-%m-%d_%H-%M-%S")
        end_stamp_str = end_stamp.strftime("%Y-%m-%d_%H-%M-%S")
        file_path = dir_path / f"{start_stamp_str}_{end_stamp_str}.csv"
        df_list[i].to_csv(file_path, index=False)

def extract_wifi_features(folder_path, save_path, config):
    sample_rate = config.wifi_sample_rate

    hash_path = os.path.join(folder_path, f"user_list.csv")
    hash_key = create_hash_key(hash_path)

    csv_paths = list(Path(folder_path).rglob("*/*.csv"))

    for csv_path in csv_paths:
        df_lists = []
        
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()

        print(f"Processing file: {csv_path}")
        
        if 'LastSeen' not in df.columns:
            print(f"Column 'LastSeen' not found in file: {csv_path}")
            continue
        
        df['LastSeen'] = pd.to_datetime(df['LastSeen'])
        time_window = df.resample(sample_rate, on='LastSeen')
        
        for window_start, window_df in time_window:
            window_df.reset_index(drop=True, inplace=True)
            window_df = extract_features(window_df, hash_key, config)
            df_lists.append(window_df)
        
        df_lists.append(csv_path.name)
        
        save_features(df_lists, save_path, sample_rate)

if __name__ == "__main__":
    rd = "DSPipeline\\Data\\Wifi_data"
    config = Config(0, 0, 0, 0, 0, 0, 0, 0, '30min', 10)
    save_path = 'test'
    
    extract_wifi_features(rd, save_path, config)
