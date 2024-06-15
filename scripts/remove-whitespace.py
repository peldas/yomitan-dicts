import os
import json

directory = '..\\KRDICT-KR-hanja'

# Iterate over each JSON file in the directory
for filename in os.listdir(directory):
    if filename.startswith('term_'):
        filepath = os.path.join(directory, filename)
        
        # Read JSON file
        f = open(filepath, 'r+', encoding='utf-8')
        
        dictionary_data = json.load(f)
        
        # Write updated content back to the JSON file
        f.seek(0)
        f.write(json.dumps(dictionary_data, ensure_ascii=False, separators=(',', ':')))
        f.truncate()
        f.close()

print("Conversion complete.")