import os
import json

directories = ['..\\KRDICT-JA-hanja', '..\\KRDICT-EN-hanja', '..\\KRDICT-KR-hanja', '..\\STDICT-hanja', '..\\Naver-JA-hanja']

for directory in directories:
    # Iterate over each JSON file in the directory
    for filename in os.listdir(directory):
        if filename.startswith('term_meta_bank_'):
            old_filepath = os.path.join(directory, filename)
            new_filepath = os.path.join(directory, 'new', filename)
            
            # Read JSON file
            old_file = open(old_filepath, 'r', encoding='utf-8')
            pronunciation_data = json.load(old_file)
            
            to_delete = []
            
            for entry in pronunciation_data:
                if not entry[2]['transcriptions'][0]['ipa']:
                    to_delete.append(entry)
            
            for entry in to_delete:
                pronunciation_data.remove(entry)
            
            # Write updated content back to the JSON file
            new_file = open(new_filepath, "w", encoding="utf-8")
            new_file.write(json.dumps(pronunciation_data, ensure_ascii=False, indent = 4))
            new_file.close()

    print("{} conversion complete.".format(directory))