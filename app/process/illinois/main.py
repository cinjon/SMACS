import app
import os

parent_directory = os.path.dirname(os.path.realpath(__file__))
documents = parent_directory + '/documents'

def get_effective_date_from_header(line):
    word_found = False
    for position, word in enumerate(line):
        if word.txt.lower() in app.utility.months:
            word_found = True
            break
    if word_found:
        return ' '.join([word.txt for word in line[position:]])
    else:
        return None

def merge_column_names(columns):
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
            new_column = app.models.Column('Generic Name',
                                           column.l, min(column.t, next_column.t),
                                           column.r, max(column.b, next_column.b))
            ret.append(new_column)
            position += 2
        elif column.title == 'Old' and next_column.title == 'SMAC':
            new_column = app.models.Column('Old Smac',
                                           column.l, min(column.t, next_column.t),
                                           column.r, max(column.b, next_column.b))
            ret.append(new_column)
            position += 2
        elif column.title == 'Label' and next_column.title == 'Name':
            new_column = app.models.Column('Label Name',
                                           column.l, min(column.t, next_column.t),
                                           column.r, max(column.b, next_column.b))
            ret.append(new_column)
            position += 2
        else:
            ret.append(column)
            position += 1
    return ret

def get_column_bounding_boxes(line):
    columns = []
    for word in line:
        columns.append(app.models.Column(word.txt,
                                         int(word.l), int(word.t),
                                         int(word.r), int(word.b)))
    return merge_column_names(columns)

def get_generic_name_words(line, next_column, len_label_words=0):
    position = len_label_words
    while(position < len(line)):
        word = line[position]
        if word.r >= next_column.l:
            break
        position += 1
    return line[len_label_words:position]

def get_label_name_words(line, next_column):
    position = 0
    while(position < len(line)):
        word = line[position]
        if word.r >= 1100:
            break
        position += 1
    return line[:position]

def get_strength_of_drug(name):
    match = app.process.regex.dose_regex.match(name)
    if not match:
        return None
    groups = match.groups()
    if groups[0]:
        return ''.join([g.strip() for g in groups[1:] if g])
    num = 0
    while (num < len(groups) and not groups[num]):
        num += 1
    if num == len(groups) - 1:
        if groups[num].split(' ')[0] == name.split(' ')[0]:
            return None
        return groups[num].strip()
    return ''.join([g.strip() for g in groups[num+1:] if g])

def get_title_of_drug(line):
    return ' '.join([w.txt for w in line])

def get_generic_name_for_specialty_drug(words, column):
    ret = []
    word = 0
    while(words[word].r < column.l):
        ret.append(words[word])
        word += 1
    return ret

forms = ['tablet', 'capsule', 'cream', 'drops', 'suspension',
         'vial', 'spray', 'ointment', 'lotion', 'syrup',
         'syringe', 'elixir', 'gel', 'powder', 'piggyback',
         'shampoo']
def get_drug_information_from_name_words(words):
    full_name = ' '.join([w.txt for w in words])
    lowercase = full_name.lower()
    strength = get_strength_of_drug(lowercase)
    for form in forms:
        if form in lowercase:
            return full_name, form.title(), strength
    return full_name, None, strength

def make_drug_line_dicts(names, lines, columns, title, date):
    ret = []
    for pos, line in enumerate(lines):
        generic_name, form, strength = get_drug_information_from_name_words(names[pos])
        assignment = {'Generic Name':generic_name, 'Form':form, 'Strength':strength}

        for word in line[len(names[pos]):]:
            for column in columns[1:]:
                if column.contains(word):
                    assignment[column.title] = word.txt
                    break
        assignment['Date'] = date
        ret.append(assignment)
    return ret

def process_generic_page(line_words, drug_start, cols, title, date):
    line_names = []
    drug_lines = []
    for line in line_words[drug_start:]:
        name = get_generic_name_words(line, cols[1], 0)
        if len(name) == 0 or app.process.regex.date_regex.match(name[0].txt):
            continue
        if len(name) == len(line): #a part of the previous line
            prev_drug_line_name = drug_lines[-1][:len(line_names[-1])]
            prev_drug_line_name.extend(name)
            prev_drug_line_name.extend(drug_lines[-1][len(line_names[-1]):])
            drug_lines[-1] = prev_drug_line_name
            line_names[-1].extend(name)
        else:
            line_names.append(name)
            drug_lines.append(line)

    return make_drug_line_dicts(line_names, drug_lines, cols, title, date), date, cols, title

def process(loc, date=None, cols=None, title=None):
    line_words = [app.process.load.get_line_words(line) for line in app.process.load.soup_ocr(loc)]
    if not title:
        title = get_title_of_drug(line_words[2])
    if not date:
        date = get_effective_date_from_header(line_words[3])
        date = app.utility.datetime_from_legible(date)

    if not cols:
        column_line = 4
        if 'Generic' in title:
            column_line += 2
        cols = get_column_bounding_boxes(line_words[column_line])

    for drug_start, line in enumerate(line_words):
        txts = [w.txt for w in line]
        if 'Price' in txts and 'Effective' in txts and 'SMAC' in txts:
            break
    drug_start = drug_start + 1

    if 'Generic' in title:
        return process_generic_page(line_words, drug_start, cols, title, date)
    # elif 'Specialty' in title:
    #     return _process_specialty(line_words, drug_start, cols, title, date)
