import app
import os

parent_directory = os.path.dirname(os.path.realpath(__file__))
documents = parent_directory + '/documents'

def has_colliding_column(column, line):
    for word in line:
        if word.r >= column.l and column.r >= word.l:
            return True, word.txt
    return False, None

def is_missing_column(prev, _next, line):
    if prev.r >= _next.l and _next.r >= prev.l: #prev and next mix
        l = min(prev.l, _next.l)
        r = max(prev.r, _next.r)
        for num, w in enumerate(line):
            if num < len(line)-1 and w.r < l and line[num+1].l > r:
                return True, num
    return False, None

list_of_headers = ['State Maximum', 'will be reimbursed', 'Upper Limit', 'Generic Name', 'Multi-Source Brand',
                   'enerlc ame', 'G _ N Current', 'Price Effective Date', '. C t SMAC']
def is_headers(line):
    line_text = ' '.join([w.txt for w in line])
    if any([k in line_text for k in list_of_headers]) or app.process.regex.legible_date_regex.match(line_text):
        return True
    return False

def is_part_of_previous_line(name_line, line, columns):
    if len(name_line) == len(line): #most of the time will work
        return True
    for word in line[len(name_line):]: #e.g. smac-list-effective-8-17-10.pdf has notes which flummox the above
        try:
            fl = float(word.txt)
            if '.' in word.txt:
                return False
        except Exception, e:
            pass
    return True

def get_drug_start(line_words):
    for drug_start, line in enumerate(line_words):
        txts = [w.txt.lower() for w in line]
        float_check = False #obv better method, use this instead prolly.
        for txt in txts:
            try:
                fl = float(txt)
                if '.' in txt:
                    float_check = True
                    break
            except Exception, e:
                pass
        next_texts = [w.txt.lower() for w in line_words[drug_start+1]]
        if ('price' in txts and 'smac' in txts) or (txts == ['proposed'] and 'effective' not in next_texts):
            break
        if float_check:
            drug_start -= 1
            break

    drug_start += 1
    return drug_start

def get_effective_date_from_header(line):
    line = ' '.join([word.txt for word in line])
    return app.utility.datetime_from_regex(line)

def get_date_and_line_number(date, line_words):
    line_number = 0
    if not date:
        while(line_number < 10):
            date = get_effective_date_from_header(line_words[line_number])
            if date:
                break
            line_number += 1
    return line_number, date

def get_columns_and_line_number(columns, line_number, line_words):
    if not columns:
        while(line_number < 10):
            line_number += 1
            line = line_words[line_number]
            line_text = [w.txt for w in line]
            if 'Generic_Name' in line_text or ('Generic' in line_text and 'Name' in line_text):
                columns = get_column_bounding_boxes(line, line_words[line_number-1], line_words[line_number+1])
                break
    return line_number, columns

def merge_column_names(columns, next_line):
    ret = []
    position = 0
    while(position < len(columns)):
        column = columns[position]
        if position == len(columns) - 1:
            if column.title == 'SMAC':
                next_line_words = [w.txt for w in next_line]
                if 'Effective' in next_line_words:
                    column.title = 'Effective Date'
                elif 'Proposed' in next_line_words:
                    column.title = 'Proposed SMAC'
            elif column.title == 'Current':
                column.title = 'SMAC'
            ret.append(column)
            position += 1
            continue

        next_column = columns[position+1]
        if column.title == 'Generic' and next_column.title == 'Name':
            new_column = app.models.Column('Generic Name',
                                           column.l, min(column.t, next_column.t),
                                           column.r, max(column.b, next_column.b))
            ret.append(new_column)
            position += 1
        elif column.title == 'Old' and next_column.title == 'SMAC':
            new_column = app.models.Column('Old SMAC',
                                           column.l, min(column.t, next_column.t),
                                           column.r, max(column.b, next_column.b))
            ret.append(new_column)
            position += 1
        elif column.title == 'Label' and next_column.title == 'Name':
            new_column = app.models.Column('Label Name',
                                           column.l, min(column.t, next_column.t),
                                           column.r, max(column.b, next_column.b))
            ret.append(new_column)
            position += 1
        elif column.title == 'Current' or column.title == 'Current.':
            if next_column.title == 'FUL':
                new_column = app.models.Column('FUL',
                                               column.l, min(column.t, next_column.t),
                                               column.r, max(column.b, next_column.b))
                ret.append(new_column)
                position += 1
            else:
                column.title = 'SMAC'
                ret.append(column)
        elif column.title == 'SMAC' and next_column.title == 'Notes' and position > 0:
            prev_title = columns[position-1].title
            has_collision, text = has_colliding_column(column, next_line)
            if has_collision:
                column.title = column.title + ' ' + text
            elif prev_title == 'Current':
                column.title = 'Effective Date'
            elif prev_title == 'Current SMAC' or prev_title == 'SMAC': #column changed from CuSrl..
                column.title = 'Proposed SMAC'
            ret.append(column)
        elif column.title == 'Current SMAC' or (column.title == 'CuSrl:ne:(t:lL' and next_column.title == 'SMAC'):
            column.title = 'SMAC'
            ret.append(column)
        elif column.title == 'Cgrint' and next_column.title == 'CuSrl:ne:(t:lL':
            column.title = 'FUL'
            ret.append(column)
        else:
            ret.append(column)
        position += 1
    return ret

def get_column_bounding_boxes(line, prev_line, next_line):
    columns = []

    for word in line:
        word.txt = word.txt.replace('0', 'O')
        txt = word.txt
        if txt in ['N', 't']: #Notes ... if we want to add it later
            continue
        if txt == 'Generic_Name':
            word.txt = 'Generic Name'
        elif txt == 'Wren':
            word.txt = 'Current'
        elif txt.replace('_', '') == 'SMAC':
            word.txt = 'SMAC'
        columns.append(app.models.Column(word.txt,
                                         int(word.l), int(word.t),
                                         int(word.r), int(word.b)))

    prev = prev_line[0]
    _next = next_line[-1]
    is_missing, column = is_missing_column(prev, _next, line)
    if is_missing:
        column += 1
        columns = columns[:column] + [
            app.models.Column(prev.txt + ' ' + _next.txt,
                              min(int(prev.l), int(_next.l)), int(prev.t),
                              max(int(prev.r), int(_next.r)), int(_next.b))
            ] + columns[column:]
    return merge_column_names(columns, next_line)

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

def make_drug_line_dicts(names, lines, columns, date):
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

def process_generic_page(line_words, drug_start, columns, date):
    line_names = []
    drug_lines = []
    start = drug_start
    if len(get_generic_name_words(line_words[drug_start], columns[1], 0)) == len(line_words[drug_start]):
        start -= 1
    for line in line_words[start:]:
        name = get_generic_name_words(line, columns[1], 0)
        if len(name) == 0 or app.process.regex.date_regex.match(name[0].txt) or is_headers(line):
            continue
        if is_part_of_previous_line(name, line, columns):
            try:
                prev_drug_line_name = drug_lines[-1][:len(line_names[-1])]
                prev_drug_line_name.extend(name)
                prev_drug_line_name.extend(drug_lines[-1][len(line_names[-1]):])
                drug_lines[-1] = prev_drug_line_name
                line_names[-1].extend(name)
            except Exception, e:
                print 'exception:'
                print ' '.join([w.txt for w in name])
                print ' '.join([w.txt for w in line])
        else:
            line_names.append(name)
            drug_lines.append(line)

    return make_drug_line_dicts(line_names, drug_lines, columns, date), date, columns, drug_start

def process(loc, date=None, columns=None, drug_start=None):
    line_words = [app.process.load.get_line_words(line) for line in app.process.load.soup_ocr(loc)]

    line_number, date = get_date_and_line_number(date, line_words)
    if not date:
        print 'No date in %s' % loc
        return [], None, None, None

    line_number, columns = get_columns_and_line_number(columns, line_number, line_words)
    if not columns:
        print 'No Columns Found: %s' % loc
        return [], None, None, None

    ## We do this everytime because the conversion isn't reliable
    drug_start = get_drug_start(line_words)

    return process_generic_page(line_words, drug_start, columns, date)
