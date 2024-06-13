import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler

file_path = r'Oura_data\Oura_raw.csv'
data = pd.read_csv(file_path)

# Fill NaN values in numeric columns with the mean of those columns
numeric_cols = data.select_dtypes(include=['number']).columns
data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].mean())

# Convert summary date to datetime format
data['summary_date'] = pd.to_datetime(data['summary_date'])

# Save the processed data 
processed_file_path = 'Oura_data/Oura_processed.csv'
data.to_csv(processed_file_path, index=False)
print("NaN values filled successfully.")