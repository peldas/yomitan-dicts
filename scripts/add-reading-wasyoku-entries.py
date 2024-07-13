import os
import json

filepath = '..\\syokudaijiten\\term_bank_2.json'

# Read JSON file
f = open(filepath, 'r+', encoding='utf-8')

dictionary_data = json.load(f)

for entry in dictionary_data:
    if entry[0].startswith('#'): # we only want to add readings to Japanese words
        continue

    definition = entry[5][0]
    reading = definition.split('\n')[1]
    entry[1] = reading

# Write updated content back to the JSON file
f.seek(0)
f.truncate()
f.write(json.dumps(dictionary_data, ensure_ascii=False, indent = 4))
f.close()

print("Conversion complete.")