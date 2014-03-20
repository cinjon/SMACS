import app
import re
import os
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup

price_regex = re.compile("^(\d+)[^\d]+(\d{5})$")
directory = os.path.dirname(os.path.realpath(__file__))
documents = directory + '/documents'

def _read_file(loc):
    try:
        f = open(loc, 'r')
        contents = f.read()
        f.close()
        return contents
    except Exception, e:
        print e

def soup_file(loc=None):
    contents = _read_file(loc)
    return BeautifulSoup(contents)

def soup_ocr(loc=None):
    soup = soup_file(loc)
    return soup.findAll('span', {'class':'ocr_line'})

def _get_word_bbox(word):
    title = word['title']
    parts = title.split(' ')
    if len(parts) < 5:
        return None
    return {'l':parts[1], 't':parts[2], 'r':parts[3], 'b':parts[4]}

def _clean_text(text):
    #list of heuristic rules to clean stuff with
    text = text.replace('|', 'I')
    if 'ELIXIR' in text and not 'ELIXIR ' in text:
        text.replace('ELIXIR', 'ELIXIR ')
    text.replace('SEROSTWI', 'SEROSTIM')
    text.replace('IWGIGT', 'MG KIT')
    text.replace('SEROSTHVI', 'SEROSTIM')
    return text

def get_line_words(line):
    ocr_words = line.findAll('span', {'class':'ocrx_word'})
    words = []
    for ocr_word in ocr_words:
        contents = ocr_word.contents
        bbox = _get_word_bbox(ocr_word)
        if not bbox:
            print 'This word has a bad box: %s' % ocr_word
            continue

        if len(contents) == 1:
            text = ocr_word.text.strip()
        else:
            text = contents[1].text.strip()

        text = _clean_text(text)
        regex = price_regex.match(text)
        if regex:
            text = '.'.join(regex.groups())
        words.append(app.models.Word(text,
                                     int(bbox['l']), int(bbox['t']),
                                     int(bbox['r']), int(bbox['b'])))
    return words
