import os
import json

directory = '..\\STDICT-hanja'

# Iterate over each JSON file in the directory
for filename in os.listdir(directory):
    if filename.startswith('term_'):
        oldfilepath = os.path.join(directory, filename)
        newfilepath = os.path.join(directory, 'new', filename)
        
        # Read JSON file
        with open(oldfilepath, 'r', encoding='utf-8') as file:
            content = json.load(file)
        
        # Write updated content back to the JSON file
        f = open(newfilepath, "w", encoding="utf-8")
        f.write(json.dumps(content, ensure_ascii=False, indent = 4))
        f.close()

print("Conversion complete.")