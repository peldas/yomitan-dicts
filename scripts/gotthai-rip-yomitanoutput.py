import requests
from bs4 import BeautifulSoup
import re
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

resume_from = 15501
last_page = 16335
batch_size = 500
final_batch_size = batch_size
last_batch = (last_page + 1) // batch_size
remainder = last_page % batch_size

for i in range(resume_from // batch_size + 1, last_batch + 1 ): 
    dictionary_data = []
    if i == last_batch and remainder != 0:
        final_batch_size += remainder
        
    for j in range (1, final_batch_size + 1):
        current_page = (i - 1) * batch_size + j

        print('Scraping {0} of {1} ({2:.2f}%)...'.format(current_page, last_page, current_page / last_page * 100))
        
        URL = "https://www.gotthai.net/th_words/{}".format(current_page)
        page = requests.get(URL)

        soup = BeautifulSoup(page.content, 'html.parser')
        
        if soup.find(string="不正なURLまたは既に削除された単語です。") != None:
            print('Page empty!')
            continue

        expressiondiv = soup.find('div', class_='thai-lg')
        expression = re.sub(r' <i.*', '', expressiondiv.decode_contents())
        
        audioURL = ''
        if soup.audio is not None:
            audioURL = 'https://www.gotthai.net' + soup.audio['src']

        pronunciation = soup.find('div', class_='pronunciation-lg').string

        katakana = ' ' + soup.find('div', class_='katakana-lg').string

        quickdefinitionlist = soup.find('table', class_='table-condensed').find_all('a')
        quickdefinitions = '\nクイック定義'
        for index, quickdefinition in enumerate(quickdefinitionlist):
            quickdefinitions += '\n{}. {}'.format(index + 1, quickdefinition.string)

        naritachistring = ''
        naritachilist = soup.find('div', class_='components-panel')
        if naritachilist != None:
            naritachilist = naritachilist.find_all('button')
            naritachistring = '\n\n成り立ち\n'
            for index, naritachi in enumerate(naritachilist):
                if naritachi.a != None:
                    thainaritachi = naritachi.a.string
                else:
                    thainaritachi = naritachi.find('div', class_="thai-sm").string
                
                japanesenaritachi = naritachi.find('div', class_='jp-meaning-sm').string
                
                if japanesenaritachi == ' ':
                    japanesenaritachi = ''
                else:
                    japanesenaritachi = ' ({})'.format(japanesenaritachi)
                
                if index != 0:
                    naritachistring += ' + '
                naritachistring += '{}{}'.format(thainaritachi, japanesenaritachi)
            
        def is_definition_div(s):
            return (s.name == 'div' and 'section' in s.get('class', []) and s.find('span') != None and s.span.string != None and s.span.string[:2] == '定義')

        def is_not_inside_table(s):
            return (s.name == 'div' and 'panel-default' in s.get('class', []) and s.parent.name != 'td')
        
        def div_parent_not_colthai(s):
            return (s.name == 'div' and 'pronunciation' in s.get('class', []) and 'col-thai' not in s.parent.get('class', []))
            
        def is_sentence_meaning(s):
            classes = s.get('class', [])
            return (s.name == 'div' and 'jp-meaning' in classes and 'jp-meaning-md' not in classes)

        breakdownlist = soup.find(is_definition_div).find_all(is_not_inside_table)
        breakdownstring = ''
        for index, breakdownelement in enumerate(breakdownlist):
            definition = '\n🇯🇵 '
            for index2, definitionpart in enumerate(breakdownelement.find('div', class_='jp-meaning-md').find_all('a')):
                if definitionpart.string == None:
                    continue
                if index2 != 0:
                    definition += ','
                definition += definitionpart.string
            
            explanation = '\n'
            if breakdownelement.p.string != None:
                explanation += breakdownelement.p.string
            examplethailists = breakdownelement.find_all('div', class_='break-word')
            examplepronunciationlist = breakdownelement.find_all(div_parent_not_colthai)
            examplejapaneselist = breakdownelement.find_all(is_sentence_meaning)
            
            exampleset = ''
            for index2, examplethailist in enumerate(examplethailists):
                examplethai = ''
                examplepronunciation = ''
                examplejapanese = ''
                
                if examplethailist != None:
                    examplethailist = examplethailist.find_all(['a', 'span'])
                    
                    for examplepart in examplethailist:
                        if examplepart.string != None:
                            examplethai += examplepart.string
                    
                    if examplethai != '':
                        examplethai = '\n🇹🇭 ' + examplethai
                        examplepronunciation = '\n' + examplepronunciationlist[index2].string
                        examplejapanese = '\n🇯🇵 ' + examplejapaneselist[index2].string
                
                if exampleset == '':
                    exampleset = '\n\n例文'
                else:
                    exampleset += '\n'
                exampleset += '{}{}{}'.format(examplethai, examplepronunciation, examplejapanese)
            
            breakdownstring += '\n\n定義 {}{}{}{}'.format(index + 1, definition, explanation, exampleset)
            
            
        content = [{ "tag": "a", "content": "ごったい", "href": URL}]
        if audioURL != '':
            content.insert(0, { "tag": "a", "content": "Audio", "href": audioURL})
        formattedJSON = { "type": "structured-content", "content": content }

        output = '{pronunciation}{katakana}{quickdefinitions}{naritachistring}{breakdownstring}\n'.format(
            expression=expression, pronunciation=pronunciation, katakana=katakana, quickdefinitions=quickdefinitions,
            naritachistring=naritachistring, breakdownstring=breakdownstring)
            
        dictionary_data.append([expression, '', '', '', 0, [output, formattedJSON], 0, ""])

    filename = "gotthai/term_bank_{}.json".format(i)
    f = open(filename, "w", encoding="utf-8")
    f.write(json.dumps(dictionary_data, ensure_ascii=False, indent = 4))
    f.close()
    print('Saved file {}, resetting array for batch {} of {}'.format(filename, i + 1, last_batch))