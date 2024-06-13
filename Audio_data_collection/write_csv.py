import csv

lists_data = []

for i in range(45, 1856):
    row = []
    row.append(f'Snore_{i}')
    row.append('sleep')
    row.append('NA')
    
    lists_data.append(row)

for i in range(11, 216):
    row = []
    row.append(f'Traffic_{i}')
    row.append('traffic')
    row.append('NA')
    
    lists_data.append(row)
    
path = r'Audio_data\data.csv'

print(lists_data)

with open(path, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(lists_data)
    
    