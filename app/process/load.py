import app
import re
import os
from BeautifulSoup import BeautifulSoup

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

def _get_hocr_bbox(hocr):
    title = hocr['title']
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

def get_all_line_words(loc):
    line_words = []
    prev_bbox = None
    #If two line_boxes have the same top, then combine those lines. They should be consecutive
    for line in app.process.load.soup_ocr(loc):
        words, bbox = app.process.load.get_line_words_and_box(line)
        if not prev_bbox:
            line_words.append(words)
        elif prev_bbox['t'] == bbox['t']:
            line_words[-1].extend(words)
        else:
            line_words.append(words)
        prev_bbox = bbox
    return line_words

def get_line_words_and_box(line):
    ocr_words = line.findAll('span', {'class':'ocrx_word'})
    words = []
    for ocr_word in ocr_words:
        contents = ocr_word.contents
        if len(contents) == 0:
            continue
        bbox = _get_hocr_bbox(ocr_word)
        if not bbox:
            print 'This word has a bad box: %s' % ocr_word
            continue

        text = _clean_text(ocr_word.text.strip())
        if text == 'Page': #Page 1 of 1, etc
            break
        regex = app.process.regex.price_regex.match(text)
        if regex:
            text = '.'.join(regex.groups())
            text = text.replace('O', '0')
        elif app.process.regex.parens_regex.match(text):
            text = '0.' + app.process.regex.parens_regex.match(text).groups()[0]
            text = text.replace('O', '0')
        words.append(app.models.Word(text,
                                     int(bbox['l']), int(bbox['t']),
                                     int(bbox['r']), int(bbox['b'])))
    return words, _get_hocr_bbox(line)
