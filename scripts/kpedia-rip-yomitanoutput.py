import requests
from bs4 import BeautifulSoup, element
import re
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

resume_from = 56501
last_page = 56534
batch_size = 500
final_batch_size = batch_size
last_batch = (last_page + 1) // batch_size
remainder = last_page % batch_size

pronunciation_string = ''
pronunciation = ''
synonym_string = ''
hanja_string = ''

dictionary_data = []

def process_batch(batch_number):
    global dictionary_data
    for j in range (1, batch_size + 1):
        current_page = (batch_number - 1) * batch_size + j
        scrape_page(current_page, last_page)
    
    filename = "../kpedia/term_bank_{}.json".format(batch_number)
    f = open(filename, "w", encoding="utf-8")
    f.write(json.dumps(dictionary_data, ensure_ascii=False, indent = 4))
    f.close()
    print('Saved file {}, resetting array for batch {} of {}'.format(filename, i + 1, last_batch))
    dictionary_data = []

def is_main_mean1_div(current_element):
    return 'main_mean1' in current_element.get('class', [])

def extract_pronunciation(pronunciation_div):
    global pronunciation_string, pronunciation, synonym_string, hanja_string
    if pronunciation_div.span is None or pronunciation_div.span.text != '読み方':
        return
    pronunciation_string = pronunciation_div.find_all('span')[2].string.strip()
    pronunciation = pronunciation_string.split('、')[0]
    
    next_sib = pronunciation_div.find_next_sibling('div')
    if not is_main_mean1_div(next_sib):
        if next_sib.span is None:
            return
        
        if next_sib.span.text == '漢字':
            hanja_div = next_sib
            hanja_string = hanja_div.find_all('span')[2].string.strip()
            next_sib = hanja_div.find_next_sibling('div')
            if is_main_mean1_div(next_sib):
                return
        
        if next_sib.span and next_sib.span.text == '類義語':
            synonym_div = next_sib
            synonym_string = synonym_div.div.get_text()
            next_sib = synonym_div.find_next_sibling('div')

def header_data(css_class):
    return css_class == 'pro_th' or css_class == 'pro_td'

def scrape_page(id, last_page):
    global pronunciation_string, pronunciation, synonym_string, hanja_string, dictionary_data
    pronunciation_string = ''
    pronunciation = ''
    synonym_string = ''
    hanja_string = ''
    
    print('\n----------Scraping {0} of {1} ({2:.2f}%)...----------\n'.format(id, last_page, id / last_page * 100))
    
    URL = "https://www.kpedia.jp/w/{}".format(id)
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')
    
    main_content = soup.find('div', id = 'mainContent')
    if main_content == None:
        print('Page empty!')
        return
    
    breadcrumb_div = main_content.td.div
    breadcrumbs = breadcrumb_div.find_all('td')[2].span.find_all('a')
    breadcrumb_string = ''
    for index, breadcrumb in enumerate(breadcrumbs):
        if index != 0:
            breadcrumb_string += ' > '
        breadcrumb_string += breadcrumb.string
        
    reading_div = breadcrumb_div.next_sibling.next_sibling
    
    if len(reading_div.a.contents) == 0: # page https://www.kpedia.jp/w/31730 has an empty term for some reason...
        print('No term!')
        return
    reading_string = reading_div.a.contents[0] # for the entry contents e.g. －(ㄴ/는)다는 것이(게)
    reading_field_string = re.sub(r'－?\[.*?\]', '', reading_string) 
    reading_field_string = re.sub(r'－?\(.*?\)', '', reading_field_string)
    reading_field_string = re.sub(r'－?\（.*?\）', '', reading_field_string)
    split_reading_strings = reading_field_string.split('/')
    formatted_reading_strings = [] # for the reading field e.g. 다는 것이
    for index, split_reading_string in enumerate(split_reading_strings):
        formatted_reading_string = split_reading_string.strip('－～ ＋')
        formatted_reading_strings.append(formatted_reading_string)
    
    imi_string = ''
    main_mean_text = ''
    example_string = ''
    profile_details = soup.find_all(class_=header_data) # handle Kpop star profiles e.g. https://www.kpedia.jp/w/25287
    if len(profile_details) != 0:
        for index, detail in enumerate(profile_details):
            if (index != 0 and index % 2 == 0) or detail.name == 'div':
                main_mean_text += '\n'
            for br in detail.find_all('br'):
                br.replace_with('\n')
            main_mean_text += detail.text.strip()
    else:
        next_sib = reading_div.find_next_sibling('div')
        
        if not is_main_mean1_div(next_sib):
            imi_div = next_sib
            imi_string = imi_div.find_all('span')[2].string.strip()
            
            pronunciation_div = imi_div.find_next_sibling('div')
            extract_pronunciation(pronunciation_div)
        
        main_mean_div = next_sib
        article_parts = soup.find_all('div', class_='article_part')
        for index, part in enumerate(article_parts):
            for a in part.find_all('a'):
                a.unwrap()
            for br in part.find_all('br'):
                br.replace_with('\n')
            for title in part.find_all('div', class_='article_title'):
                title.append('\n')
            for comment in part.find_all('div', class_='article_comment'):
                comment.decompose()
            
            part_text = part.text.strip()
            if index != 0 and part_text != '':
                main_mean_text += '\n\n\n'
            main_mean_text += part_text.replace('\n\n\n', '\n\n')
        
        # Kpedia devs broke their HTML after this section so we need to use hacky ways to find the next elements
        
        if not pronunciation_string:
            pronunciation_div = soup.find(string=lambda text: isinstance(text, element.Comment) and text.strip().find('単語') > -1).find_next_sibling('div')
            extract_pronunciation(pronunciation_div)
        
        next_sib = soup.find(string=lambda text: isinstance(text, element.Comment) and text.strip().find('例文') > -1).next_sibling.next_sibling
        
        if next_sib.text.startswith('例文') or next_sib.text.endswith('例文'):
            example_table = next_sib.find_next_sibling('table')
            for index, tr in enumerate(example_table.find_all('tr')):
                flags = ['🇰🇷', '🇯🇵']
                if index != 0:
                    example_string += '\n'
                rowText = tr.get_text(strip=True)
                if rowText.endswith('の例文をすべてを見る'):
                    break
                example_string += '{} {}'.format(flags[index % 2], rowText)
    
    split_pronunciation_strings = pronunciation.split('/')
    for i in range(len(split_pronunciation_strings)):
        split_pronunciation_strings[i] = split_pronunciation_strings[i].strip('－～ ＋')
    
    output = reading_string
    if imi_string:
        output += '\n意味: {}'.format(imi_string)
    if pronunciation_string:
        output+= '\n読み方: {}'.format(pronunciation_string)
    if hanja_string:
        output += '\n漢字: {}'.format(hanja_string)
    if synonym_string:
        output += '\n類義語: {}'.format(synonym_string)
    if main_mean_text:
        output += '\n\n{}'.format(main_mean_text)
    if example_string:
        output += '\n\n'
        if imi_string:
            output += '「{}」の韓国語「{}」を使った例文'.format(imi_string, reading_string)
        else:
            output += '例文・会話'
        output += '\n{}'.format(example_string)
    if breadcrumb_string:
        output += '\n\n{}'.format(breadcrumb_string)
    
    content = [{ "tag": "a", "content": "Kpedia", "href": URL}]
    formattedJSON = { "type": "structured-content", "content": content }
    
    for index, formatted_reading_string in enumerate(formatted_reading_strings):
        if len(split_pronunciation_strings) < index + 1:
            pronunciation = split_pronunciation_strings[0]
        else:
            pronunciation = split_pronunciation_strings[index]
        dictionary_data.append([formatted_reading_strings[index], pronunciation, '', '', 0, [output, formattedJSON], id, ""])

#scrape_page(45032, 45032)

for i in range(resume_from // batch_size + 1, last_batch + 1 ):
    if i == last_batch and remainder != 0:
        final_batch_size = remainder
        
    process_batch(i)
    