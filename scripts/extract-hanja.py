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
        
        hanja = termReadingGroup[1]['content']
        
        if hanja == '' or hanja.isnumeric():
            continue
        
        hanja = hanja.strip(' 〔〕')
        
        result = re.search('[a-zA-Z]', hanja)
        if result is not None:
            continue
        
        i[1] = i[0]
        i[0] = hanja
        
    processedfile = dictdir + 'processed\\' + filename
    f = open(processedfile, "w", encoding = "utf-8")
    f.write(json.dumps(data, indent = 4))
    f.close()
    print('Saved file ' + processedfile)