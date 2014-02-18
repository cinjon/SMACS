import re
import files
from models import Word
from models import Column

date_regex  = re.compile("^(\d{1,2})/(\d{1,2})/(\d{4})$")

def clean_text(text):
    #list of heuristic rules to clean stuff with
    if 'EL|X|R' in text:
        parts = text.split('EL|X|R')
        text = parts[0] + 'ELIXIR' + parts[1]
    return text

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
        else:
            ret.append(column)
            position += 1
    return ret

def get_col_bboxes(line):
    columns = []
    for word in line:
        columns.append(Column(word.txt, int(word.l), int(word.t), int(word.r), int(word.b)))
    return clean_columns(columns)

def get_generic_name(line, next_column):
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

def process(loc):
    line_words = [files.get_line_words(line) for line in files.soup_ocr(loc)]
    effective_date = get_effective_date(line_words[3])
    col_bboxes = get_col_bboxes(line_words[6])

    line_names = []
    drug_lines = []
    for line in line_words[8:]:
        name = get_generic_name(line, col_bboxes[1])
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

    assigned_lines = assign_lines(line_names, drug_lines, col_bboxes)
    return effective_date, col_bboxes, assigned_lines

if __name__ == '__main__':
    files.soup_file()
