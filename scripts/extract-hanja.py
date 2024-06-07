import os
import json
import re

dictdir = '..\\KRDICT-JA-hanja\\'

for filename in os.listdir(dictdir):
    if filename == 'index.json' or filename == 'processed':
        continue
    
    file = open(dictdir + filename, "r", encoding = 'utf-8')
    data = json.load(file)
    
    for i in data:
        termReadingGroup = i[5][0]['content'][0]['content']
        if len(termReadingGroup) < 2:
            continue
        
        for content in termReadingGroup:
            hanja = content['content']
        
            if re.search('〔', hanja) is None:
                continue
        
            hanja = hanja.strip(' 〔〕')
        
            i[1] = i[0]
            i[0] = hanja
            
            break
        
        
    processedfile = dictdir + 'processed\\' + filename
    f = open(processedfile, "w", encoding = "utf-8")
    f.write(json.dumps(data, indent = 4))
    f.close()
    print('Saved file ' + processedfile)