import os
import json
import re

directory = '..\\kpedia\\processed\\new'

# Iterate over each JSON file in the directory
for filename in os.listdir(directory):
    if filename.startswith('term_'):
        oldfilepath = os.path.join(directory, filename)
        newfilepath = os.path.join(directory, 'fixed', filename)
        
        # Read JSON file
        old_file = open(oldfilepath, 'r', encoding='utf-8')
        dictionary_data = json.load(old_file)
        new_data = []
        
        for entry in dictionary_data:
            # remove extra translations from example sentences heading
            entry[5][0] = re.sub(r'、.*?(?=」の韓国語「.*?」を使った例文)', '', entry[5][0])
            pronunciation_string = re.search(r'(?<=読み方: ).*?(?=、)', entry[5][0])
            if pronunciation_string == None:
                pronunciation_string = entry[1]
            else:
                pronunciation_string = pronunciation_string.group(0)
        
            # fix readings and create duplicate entries for slashed readings
            reading_string = entry[0]
            reading_string = re.sub(r'－?\[.*?\]', '', reading_string) 
            reading_string = re.sub(r'－?\(.*?\)', '', reading_string)
            reading_string = re.sub(r'－?\（.*?\）', '', reading_string)
            split_reading_strings = reading_string.split('/')
            formatted_reading_strings = [] # for the reading field e.g. 다는 것이
            for split_string in split_reading_strings:
                formatted_reading_string = split_string.strip('－～ ＋')
                #formatted_reading_string = re.sub(r'－?\[.*?\]', '', formatted_reading_string) 
                #formatted_reading_string = re.sub(r'－?\(.*?\)', '', formatted_reading_string)
                #formatted_reading_string = re.sub(r'－?\（.*?\）', '', formatted_reading_string)
                formatted_reading_strings.append(formatted_reading_string)
            
            pronunciation_string = re.sub(r'－?\[.*?\]', '', pronunciation_string) 
            pronunciation_string = re.sub(r'－?\(.*?\)', '', pronunciation_string)
            pronunciation_string = re.sub(r'－?\（.*?\）', '', pronunciation_string)
            split_pronunciation_strings = pronunciation_string.split('/')
            for i in range(len(split_pronunciation_strings)):
                split_pronunciation_strings[i] = split_pronunciation_strings[i].strip('－～ ＋')
            
            for index, formatted_reading_string in enumerate(formatted_reading_strings):
                if index == 0:
                    entry[0] = formatted_reading_string
                    entry[1] = split_pronunciation_strings[0]
                    continue
                new_entry = entry.copy()
                new_entry[0] = formatted_reading_string
                if len(split_pronunciation_strings) < index + 1:
                    new_entry[1] = split_pronunciation_strings[0]
                else:
                    new_entry[1] = split_pronunciation_strings[index]
                new_data.append(new_entry)
                print('Added new entry for {} to file {}'.format(formatted_reading_string, filename))
        
        dictionary_data.extend(new_data)
        # Write updated content back to the JSON file
        new_file = open(newfilepath, "w", encoding="utf-8")
        new_file.write(json.dumps(dictionary_data, ensure_ascii=False, indent = 4))
        new_file.close()

print("Conversion complete.")