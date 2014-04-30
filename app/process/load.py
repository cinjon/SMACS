import app
import re
import os
from BeautifulSoup import BeautifulSoup

price_regex = re.compile("^([\d*O*\d*]+)[^\d]+([\d*O*]{4,5})$") #so not robust, ugh.
parens_regex = re.compile("^\(1([\d*0*]{5})$") #sometimes, 0 looks like (1 to ghostscript
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

cleaning_instructions = [
    ['SEROSTWI','SEROSTIM'], ['IWGIGT','MG KIT'], ['SEROSTHVI','SEROSTIM'],
    ['|','I'], ['GenerIc_Name', 'Generic_Name'], ['I(33IPERACILLIN', 'PIPERACILLIN'],
    ['MG&quot;', 'MG'], ['&quot;', '"']
]
def _clean_text(text):
    #list of heuristic rules to clean stuff with
    for instruction in cleaning_instructions:
        text = text.replace(instruction[0], instruction[1])
    if 'ELIXIR' in text and not 'ELIXIR ' in text:
        text = text.replace('ELIXIR', 'ELIXIR ')
    return text

def get_line_words(line):
    ocr_words = line.findAll('span', {'class':'ocrx_word'})
    words = []
    for ocr_word in ocr_words:
        contents = ocr_word.contents
        if len(contents) == 0:
            continue
        bbox = _get_word_bbox(ocr_word)
        if not bbox:
            print 'This word has a bad box: %s' % ocr_word
            continue

        text = _clean_text(ocr_word.text.strip())
        if text == 'Page': #Page 1 of 1, etc
            break
        regex = price_regex.match(text)
        if regex:
            text = '.'.join(regex.groups())
        elif parens_regex.match(text):
            text = '0.' + parens_regex.match(text).groups()[0]
        text = text.replace('O', '0')
        words.append(app.models.Word(text,
                                     int(bbox['l']), int(bbox['t']),
                                     int(bbox['r']), int(bbox['b'])))
    return words
