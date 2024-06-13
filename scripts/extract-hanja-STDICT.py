import os
import json
import re

dictdir = '..\\STDICT-hanja\\'
processeddir = dictdir + 'processed\\'

for filename in os.listdir(dictdir):
    if filename == 'index.json' or filename == 'processed':
        continue
    
    term_bank_file = open(dictdir + filename, "r", encoding = 'utf-8')
    term_bank_data = json.load(term_bank_file)
    
    term_meta_bank_data = []
    
    for i in term_bank_data:
        reading = i[0]
        pronunciation = i[1]
        if pronunciation == '':
            pronunciation = reading
        i[1] = reading # pronunciations are now stored in the IPA field so we should make this field consistently show reading for both hanja and hangul words
        termReadingGroup = i[5][0]['content'][0]['content']
        
        if len(termReadingGroup) >= 2:
            for content in termReadingGroup:
                hanja = content['content']
            
                if re.search('〔', hanja) is None:
                    continue
            
                hanja = hanja.strip(' 〔〕')
                i[0] = hanja
                
                break
        
        # hack the IPA field to contain hangul pronunciations
        term_meta_bank_data.append([i[0], 'ipa', {
            'reading': reading,
            'transcriptions': [
                {
                    'ipa': pronunciation,
                    'tags': []
                }
            ]
        }])
        
    processedfilepath = processeddir + filename
    f = open(processedfilepath, 'w', encoding = 'utf-8')
    f.write(json.dumps(term_bank_data, indent = 4))
    f.close()
    print('Saved file ' + processedfilepath)
    
    term_meta_bank_filepath = processeddir + 'term_meta_bank_' + filename.split('_')[2]
    term_meta_bank_file = open(term_meta_bank_filepath, 'w', encoding = 'utf-8')
    term_meta_bank_file.write(json.dumps(term_meta_bank_data, ensure_ascii=False, indent = 4))
    term_meta_bank_file.close()
    print('Saved file ' + term_meta_bank_filepath)