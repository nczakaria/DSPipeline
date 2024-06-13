import scipy.io
import pandas as pd
import os
import csv
import numpy as np
import datetime



def convert_to_normal_array(nested_array):
    normal_array = []
    for item in nested_array:
        # Check if the array is empty
        if item[0][0].size == 0:
            normal_array.append('[]')
        else:
            normal_array.append(item[0][0])
    return normal_array
    
# Load the .mat file
mat_file_path = r'Tap_Data\TapData.mat'
mat_data = scipy.io.loadmat(mat_file_path)

# Extract fields
users = mat_data['TapData']['Users'][0][0]
bins = mat_data['TapData']['bins'][0][0]       
sleep_sum = mat_data['TapData']['SleepSum'][0][0]  

# Ask the user for the directory to save CSV files
output_directory = r"Tap_Data"


users = convert_to_normal_array(users)

#print(users)


def feature_extraction(user, idx, bins, sleep_sum):
    # Bin tap counts
    time_stamp_dictionary = {}
    for i in range(1, 4):
        
        np_array = bins[idx][i]
        #print(np_array.shape)   
        #print(len(np_array))
        for j in range(len(np_array)):
            if type( bins[idx][i][j][0]) == np.float64:
                posix_time = bins[idx][i][j][0] / 1000.0
                date = datetime.datetime.fromtimestamp(posix_time)
            else:
                date = datetime.datetime.strptime(bins[idx][i][j][0][0] , '%d-%b-%Y')
            date = date.strftime('%Y-%m-%d %H:%M:%S')
            tap_count = bins[idx][i][j][1]
        
            if date in time_stamp_dictionary:
                time_stamp_dictionary[date][i - 1] = tap_count
            else:
                time_stamp_dictionary[date] = [0, 0, 0]
                time_stamp_dictionary[date][i - 1] = tap_count
        
        #print(time_stamp_dictionary)
    
    # Sleep sum
    day_dictionary = {}
    for i in range(len(sleep_sum['BT'][0][0][0])):
        bt, wt, tib = None, None, None
        if not np.isnan(sleep_sum['BT'][0][0][idx][i]):
            bt = datetime.datetime.fromtimestamp(sleep_sum['BT'][0][0][idx][i]).strftime('%Y-%m-%d %H:%M:%S')
        if not np.isnan(sleep_sum['WT'][0][0][idx][i]):
            wt = datetime.datetime.fromtimestamp(sleep_sum['WT'][0][0][idx][i]).strftime('%Y-%m-%d %H:%M:%S')
        if not np.isnan(sleep_sum['TIB'][0][0][idx][i]):
            tib = sleep_sum['TIB'][0][0][idx][i]
        
        day_dictionary[i + 1] = [bt, wt, tib]
        
    print (day_dictionary)
    return time_stamp_dictionary, day_dictionary
    
    


def get_start_date(time_stamp_dict):
    sorted_dates = sorted(time_stamp_dict.keys())
    start_date_str = sorted_dates[0]
    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
    return start_date

def merge_dictionaries(time_stamp_dict, day_dict, start_date):
    merged_list = []
    for date_str in sorted(time_stamp_dict.keys()):
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        day_diff = (date - start_date).days + 1  # Calculate the day number
        bt, wt, tib = day_dict.get(day_diff, [None, None, None])
        merged_list.append([date_str] + time_stamp_dict[date_str] + [day_diff, bt, wt, tib])
    
    return merged_list
# Iterate through the users
for i, user in enumerate(users):
    if user == '[]':
        continue
    else:
        time_stamp_dictionary, day_dictionary = feature_extraction(user, i, bins, sleep_sum)
        start_date = get_start_date(time_stamp_dictionary)
        merged_list  = merge_dictionaries(time_stamp_dictionary, day_dictionary, start_date)
        
        with open(f'{output_directory}/{user}.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Bin_1_min', 'Bin_30_min', 'Bin_24_hr', 'Day', 'BT', 'WT', 'TIB'])
            for row in merged_list:
                writer.writerow(row)

print("CSV files have been created.")