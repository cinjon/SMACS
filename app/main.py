import re
import load
import ocr
import os
from models import Column

date_regex  = re.compile("^(\d{1,2})/(\d{1,2})/(\d{4})$")

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']
def get_effective_date(line):
    word_found = False
    for position, word in enumerate(line):
        if word.txt in months:
            word_found = True
            break
    if word_found:
        return ' '.join([word.txt for word in line[position:]])
    else:
        return None

def clean_columns(columns):
    ret = []
    position = 0
    while(position < len(columns)):
        column = columns[position]
        if position == len(columns) - 1:
            if column.title == 'SMAC':
                column.title = 'Effective Date'
            ret.append(column)
            position += 1
            continue

        next_column = columns[position+1]
        if column.title == 'Generic' and next_column.title == 'Name':
            new_column = Column('Generic Name',
                                column.l, min(column.t, next_column.t),
                                column.r, max(column.b, next_column.b))
            ret.append(new_column)
            position += 2
        elif column.title == 'Old' and next_column.title == 'SMAC':
            new_column = Column('Old Smac',
                                column.l, min(column.t, next_column.t),
                                column.r, max(column.b, next_column.b))
            ret.append(new_column)
            position += 2
        elif column.title == 'Label' and next_column.title == 'Name':
            new_column = Column('Label Name',
                                column.l, min(column.t, next_column.t),
                                column.r, max(column.b, next_column.b))
            ret.append(new_column)
            position += 2
        else:
            ret.append(column)
            position += 1
    return ret

def get_col_bboxes(line):
    columns = []
    for word in line:
        columns.append(Column(word.txt, int(word.l), int(word.t), int(word.r), int(word.b)))
    return clean_columns(columns)

def get_name(line, next_column):
    position = 0
    while(position < len(line)):
        word = line[position]
        if word.r >= next_column.l:
            break
        position += 1
    return line[:position]

def assign_lines(names, lines, columns):
    ret = []
    for pos, line in enumerate(lines):
        assignment = {'Generic Name':' '.join([w.txt for w in names[pos]])}
        for word in line[len(names[pos]):]:
            for column in columns[1:]:
                if column.contains(word):
                    assignment[column.title] = word.txt
                    break
        ret.append(assignment)
    return ret

def get_title(line):
    return ' '.join([w.txt for w in line])

def process(loc, date=None, cols=None, title=None):
    line_words = [load.get_line_words(line) for line in load.soup_ocr(loc)]
    if not title:
        title = get_title(line_words[2])
    if not date:
        date = get_effective_date(line_words[3])

    column_line = 4
    if 'Generic' in title:
        column_line += 2
    if not cols:
        cols = get_col_bboxes(line_words[column_line])

    line_names = []
    drug_lines = []
    for line in line_words[(2+column_line):]:
        name = get_name(line, cols[1])
        if len(name) == 0 or date_regex.match(name[0].txt):
            continue
        if len(name) == len(line): #really a part of the previous one
            prev_drug_line_name = drug_lines[-1][:len(line_names[-1])]
            prev_drug_line_name.extend(name)
            prev_drug_line_name.extend(drug_lines[-1][len(line_names[-1]):])
            drug_lines[-1] = prev_drug_line_name
            line_names[-1].extend(name)
        else:
            line_names.append(name)
            drug_lines.append(line)

    assigned_lines = assign_lines(line_names, drug_lines, cols)
    return assigned_lines, date, cols, title, line_names, drug_lines

def process_hocr_dir(directory):
    assignments = []
    date = None
    cols = None
    title = None
    for f in os.listdir(directory):
        print f
        if f == 'done':
            continue
        page_assignments, date, cols = process(directory + f, date, cols)
        assignments.extend(page_assignments)
#         ocr.done_file(directory, f)
    return assignments, date, cols

def process_dir(directory):
    #assumes directory has:
    #/src with pdfs to process, /decrypted, /png, /hocr
    src = directory + '/src/'
    decrypted = directory + '/decrypted/'
    png = directory + '/png/'
    hocr = directory + '/hocr/'

    for f in os.listdir(src):
        if f == 'done':
            continue
        ocr.decrypt_pdf(src, decrypted, f)
        ocr.done_file(src, f)

        ocr.ghostscript_pdf_to_png(decrypted, png, f)
        ocr.done_file(decrypted, f)

        for png_f in os.listdir(png):
            ocr.tesseract_png_to_hocr(png, hocr, png_f)
            ocr.done_file(png, png_f)

if __name__ == '__main__':
    load.soup_file()