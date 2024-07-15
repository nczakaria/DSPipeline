import csv


file_path = r"Audio\unbalanced_train_segments.csv"
audio_type = 'human_noise'
snoring_rows = []

with open(file_path, 'r', newline='') as file:
    csv_reader = csv.reader(file)
    header = next(csv_reader)
    
    for row in csv_reader:
        #if '/m/01d3sd' in row[3] and '/m/0jbk' not in row[3]:
        if '/m/09l8g' in row[3]:
            snoring_rows.append([row[0], row[1], row[2]])  

save_file_path = f"Audio\{audio_type}_data.csv"
with open(save_file_path, 'w', newline='') as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(['URL', 'Start Time', 'End Time'])  
    csv_writer.writerows(snoring_rows)

print(snoring_rows[:10])  
