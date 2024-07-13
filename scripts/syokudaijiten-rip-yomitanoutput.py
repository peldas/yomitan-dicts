import requests
from bs4 import BeautifulSoup, element
import re
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

resume_from = 8001
last_page = 8053
batch_size = 1000
last_batch = (last_page + 1) // batch_size
remainder = last_page % batch_size

# colour name may not exist, in which case we just have a hex code https://www.colordic.org/colorsample/7000
# 404 is just a page with "NOT FOUND" inside a series of nested divs https://www.colordic.org/colorsample/6800
# "reading" can be English so we should just put it in the definition instead https://www.colordic.org/colorsample/5006

dictionary_data = []

def process_batch(batch_number):
    global dictionary_data
    for j in range (1, batch_size + 1):
        current_page = (batch_number - 1) * batch_size + j
        if current_page > last_page:
            break
        scrape_page(current_page, last_page)
    
    filename = "../syokudaijiten/term_bank_{}.json".format(batch_number)
    f = open(filename, "w", encoding="utf-8")
    f.write(json.dumps(dictionary_data, ensure_ascii=False, indent = 4))
    f.close()
    dictionary_data = []

def scrape_page(id, last_page):
    global dictionary_data
    output = {}
    
    print('\n----------Scraping {0} of {1} ({2:.2f}%)...----------\n'.format(id, last_page, id / last_page * 100))
    
    URL = "https://www.colordic.org/colorsample/{}".format(id)
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')
    
    if soup.find(string='Not Found') != None:
        print('Page empty!')
        return
    
    detail_div = soup.find('div', class_='detail')
    current_heading = detail_div.h1
    if not current_heading.text.startswith('#'): # colour name populated
        colour_breakdown = current_heading.text.split(' ')
        output['colour_name'] = colour_breakdown[0]
        output['colour_reading'] = ' '.join(colour_breakdown[1:])
        current_heading = current_heading.find_next_sibling('h1')
    
    output['hex_code'] = current_heading.text
    
    current_heading = current_heading.find_next_sibling('h2')
    output['description'] = current_heading.text
    
    current_heading = current_heading.find_next_sibling('h2')
    output['rgb'] = current_heading.text
    
    current_heading = current_heading.find_next_sibling('h2')
    output['hsb'] = current_heading.text
    
    current_heading = current_heading.find_next_sibling('h2')
    output['lab'] = current_heading.text
    
    current_heading = current_heading.find_next_sibling('h2')
    output['cmyk'] = current_heading.text
    
    current_heading = current_heading.find_next_sibling('h2')
    output['explanation'] = current_heading.text
    
    entry = ''
    if output.get('colour_reading'):
        entry = output['colour_reading'] + '\n'
    entry += '\n'.join([output['hex_code'], output['description'], output['rgb'], output['hsb'], output['lab'], output['cmyk'], output['explanation']])
    
    content = [{ "tag": "a", "content": "洋色大辞典", "href": URL}]
    content.insert(0, { "tag": "span",
                        "style": {
                            "backgroundColor": output['hex_code'],
                            "padding": "0px 10px 0px 10px",
                            "margin": "0px 10px 0px 10px"
                        }})

    mediaJSON = { "type": "structured-content", "content": content }
    
    if output.get('colour_name'):
        entry = '\n'.join([output['colour_name'], entry])
        dictionary_data.append([output['colour_name'], '', '', '', 0, [entry, mediaJSON], id, ''])
    
    dictionary_data.append([output['hex_code'], '','','', 0, [entry, mediaJSON], id, ''])


for i in range(resume_from // batch_size + 1, last_batch + 1 ):
    if i == last_batch and remainder != 0:
        final_batch_size = remainder
        
    process_batch(i)