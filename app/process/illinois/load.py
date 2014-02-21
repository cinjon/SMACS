import re
import app
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup

price_regex = re.compile("^(\d+)[^\d]+(\d{5})$")
illinois = app.basedir + '/illinois'

def read_file(loc):
    try:
        f = open(loc, 'r')
        contents = f.read()
        f.close()
        return contents
    except Exception, e:
        print e

def soup_file(loc=None):
    loc = loc or location
    contents = read_file(loc)
    return BeautifulSoup(contents)

def soup_ocr(loc=None):
    loc = loc or location
    soup = soup_file(loc)
    return soup.findAll('span', {'class':'ocr_line'})

def get_word_bbox(word):
    title = word['title']
    parts = title.split(' ')
    if len(parts) < 5:
        print 'wrogn # of parts'
        return None
    return {'l':parts[1], 't':parts[2], 'r':parts[3], 'b':parts[4]}

def clean_text(text):
    #list of heuristic rules to clean stuff with
    text = text.replace('|', 'I')
    if 'ELIXIR' in text and not 'ELIXIR ' in text:
        text.replace('ELIXIR', 'ELIXIR ')
    return text

def get_line_words(line):
    ocr_words = line.findAll('span', {'class':'ocrx_word'})
    words = []
    for ocr_word in ocr_words:
        contents = ocr_word.contents
        bbox = get_word_bbox(ocr_word)
        if not bbox:
            print 'This word has a bad box: %s' % ocr_word
            continue

        if len(contents) == 1:
            try:
                text = contents[0].strip()
            except Exception:
                text = contents[0].contents[0].strip()
        else:
            text = contents[1].contents[0].strip()

        regex = price_regex.match(text)
        if regex:
            text = '.'.join(regex.groups())
        else:
            text = clean_text(text)
        words.append(
            app.models.Word(
                text, int(bbox['l']), int(bbox['t']), int(bbox['r']), int(bbox['b'])
                )
            )
    return words