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

def is_part_of_previous_line(name_line, line):
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
                if '.' in txt and not any([month in txts for month in app.utility.months]):
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

def get_columns_and_line_number(columns, line_number, line_words, type_file):
    if not columns:
        while(line_number < 10):
            line_number += 1
            line = line_words[line_number]
            line_text = [w.txt for w in line]
            if 'Generic_Name' in line_text or ('Generic' in line_text and 'Name' in line_text) or ('L' in line_text and 'b' in line_text and 'G' in line_text):
                #last clause is because some of the specialtys get really fucked up
                columns = get_column_bounding_boxes(line, line_words[line_number-1], line_words[line_number+1], type_file)
                break
    return line_number, columns

def get_start_of_generic(drug_lines):
    lefts = [w.l for w in drug_lines]

def get_type_of_file(loc, line_words, drug_start):
    if 'proposed' in loc:
        return 'proposed'
    elif 'special' in loc:
        return 'label'

    for line in line_words[:drug_start]:
        line_text = ' '.join([w.txt for w in line]).lower()
        if 'generic' in line_text:
            return 'generic'
    return 'unknown type'

def merge_column_names(columns, next_line, type_file):
    ret = []
    position = 0
    while(position < len(columns)):
        column = columns[position]
        if position == len(columns) - 1:
            if column.title == 'SMAC' and 'Effective' in [w.txt for w in next_line]:
                column.title = 'Effective Date'
            elif column.title == 'Current':
                column.title = 'SMAC'
            elif column.title =='SMAC' and type_file == 'proposed':
                column.title = 'Proposed SMAC'
            ret.append(column)
            position += 1
            continue

        next_column = columns[position+1]
        if column.title == 'Generic' and next_column.title == 'Name':
            new_column = app.models.Column('Generic Name',
                                           column.l, min(column.t, next_column.t),
                                           next_column.r, max(column.b, next_column.b))
            ret.append(new_column)
            position += 1
        elif column.title == 'Old' and next_column.title == 'SMAC':
            new_column = app.models.Column('Old SMAC',
                                           column.l, min(column.t, next_column.t),
                                           next_column.r, max(column.b, next_column.b))
            ret.append(new_column)
            position += 1
        elif column.title == 'Label' and next_column.title == 'Name':
            new_column = app.models.Column('Label Name',
                                           column.l, min(column.t, next_column.t),
                                           next_column.r, max(column.b, next_column.b))
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
    if len(next_line) == 1 and next_line[0].txt == 'Proposed' and next_line[0].l > columns[-1].r:
        col = next_line[0]
        ret.append(app.models.Column('Proposed SMAC', col.l, col.t, col.r, col.b))
    return ret

def get_column_bounding_boxes(line, prev_line, next_line, type_file, debug=False):
    columns = []

    if ' '.join([w.txt for w in line]) == 'L b I N G _ N Old SMAC Current SMAC':
        label_word = app.models.Word('Label Name', line[0].l, line[0].t, line[3].r, next_line[0].b)
        generic_word = app.models.Word('Generic Name', line[4].l, line[4].t, line[6].r, next_line[0].b)
        temp = line[7:]
        line = [label_word, generic_word]
        line.extend(temp)

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
    if debug:
        return columns
    return merge_column_names(columns, next_line, type_file)

def get_generic_name_words(line, next_column, len_label_words=0):
    position = len_label_words
    while(position < len(line)):
        word = line[position]
        if word.r >= next_column.l:
            break
        position += 1
    return line[len_label_words:position]

def get_label_name_words(line):
    generic_start_left = 1090 #it's really 1100, but we put a buffer jjjjjust in case
    return [word for word in line if word.l < generic_start_left]

def get_title_of_drug(line):
    return ' '.join([w.txt for w in line])

def get_generic_name_for_label_drug(words, column):
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
def get_drug_information_from_name_words(generic_words, label_words):
    def get_name_and_strength_of_drug(text):
        match = app.process.regex.dose_regex.match(text.lower())
        if not match:
            return text, None
        groups = match.groups()
        if groups[0]:
            # the name is first. everything after we consider strength
            return text[:len(groups[0])], ''.join([g.strip() for g in groups[1:] if g])
        num = 0
        while (num < len(groups) and not groups[num]):
            # find where the name is
            num += 1
        if num == len(groups) - 1:
            # is it at the end? if so, make sure that there is a strength
            if groups[num].split(' ')[0] == text.lower().split(' ')[0]:
                return text, None
            return text, groups[num].strip()
        return text[:len(groups[num])], ''.join([g.strip() for g in groups[num+1:] if g])

    def get_form_of_drug(text):
        text = text.lower()
        for form in forms:
            if form in text:
                return form.title()
        return None

    generic_word_text = ' '.join([w.txt for w in generic_words])
    form = get_form_of_drug(generic_word_text)

    # Get generic name and strength
    generic_name, strength = get_name_and_strength_of_drug(generic_word_text)

    # Get label name if necessary. Supply a strength if not already found
    label_name = None
    if label_words:
        label_name, label_strength = get_name_and_strength_of_drug(' '.join([w.txt for w in label_words]))
        strength = strength or label_strength

    return generic_name, label_name, form, strength

def make_drug_line_dicts(label_names, generic_names, lines, columns, date):
    ret = []
    for pos, line in enumerate(lines):
        generic_name, label_name, form, strength = get_drug_information_from_name_words(generic_names[pos], label_names[pos])
        assignment = {'Generic Name':generic_name, 'Form':form, 'Strength':strength}
        if label_name:
            assignment['Label Name'] = label_name

        for word in line[len(generic_names[pos]) + len(label_names[pos]):]:
            for column in columns[1:]:
                if column.contains(word):
                    assignment[column.title] = word.txt
                    break
        assignment['Date'] = date
        ret.append(assignment)
    return ret

def process_label_page(line_words, drug_start, columns, date):
    label_names = []
    generic_names = []
    drug_lines = []

    for line in line_words[drug_start:]:
        label_name = get_label_name_words(line)
        if len(label_name) == 0 or app.process.regex.date_regex.match(label_name[0].txt) or is_headers(line):
            continue

        generic_name = get_generic_name_words(line, columns[2], len(label_name))
        names_of_line = []
        names_of_line.extend(label_name)
        names_of_line.extend(generic_name)

        if is_part_of_previous_line(names_of_line, line):
            try:
                prev_label_name = label_names[-1]
                prev_generic_name = generic_names[-1]
                drug_lines[-1] = prev_label_name + label_name + prev_generic_name + generic_name + drug_lines[-1][len(prev_label_name) + len(prev_generic_name):]
                generic_names[-1].extend(generic_name)
                label_names[-1].extend(label_name)
            except Exception, e:
                print 'exception:'
                print 'line: %s' % ' '.join([w.txt for w in line])
                print 'label: %s' % ' '.join([w.txt for w in label_name])
                print 'generic: %s' % ' '.join([w.txt for w in generic_name])
        else:
            label_names.append(label_name)
            generic_names.append(generic_name)
            drug_lines.append(line)
    return make_drug_line_dicts(label_names, generic_names, drug_lines, columns, date)

def process_proposed_page(line_words, drug_start, columns, date):
    pass

#TODO: Refactor the shit out of this.
def process_generic_page(line_words, drug_start, columns, date):
    line_names = []
    drug_lines = []

    if len(get_generic_name_words(line_words[drug_start], columns[1])) == len(line_words[drug_start]):
        #why did we do this? i don't even...
        drug_start -= 1
    for line in line_words[drug_start:]:
        name = get_generic_name_words(line, columns[1])
        if len(name) == 0 or app.process.regex.date_regex.match(name[0].txt) or is_headers(line):
            continue
        if is_part_of_previous_line(name, line):
            try:
                prev_drug_line_name = drug_lines[-1][:len(line_names[-1])] #prev generic_name
                prev_drug_line_name.extend(name) #add on this generic_name
                prev_drug_line_name.extend(drug_lines[-1][len(line_names[-1]):]) #add on rest of line
                drug_lines[-1] = prev_drug_line_name
                line_names[-1].extend(name)
            except Exception, e:
                print 'exception:'
                print ' '.join([w.txt for w in name])
                print ' '.join([w.txt for w in line])
        else:
            line_names.append(name)
            drug_lines.append(line)
    return make_drug_line_dicts([[] for i in range(len(line_names))], line_names, drug_lines, columns, date)

def process(loc, date=None, columns=None, drug_start=None, type_file=None):
    line_words = app.process.load.get_all_line_words(loc)

    line_number, date = get_date_and_line_number(date, line_words)
    if not date:
        print 'No date in %s' % loc
        return [], None, None, None

    ## We do this everytime because the conversion isn't reliable
    drug_start = get_drug_start(line_words)

    if not type_file:
        type_file = get_type_of_file(loc, line_words, drug_start)

    line_number, columns = get_columns_and_line_number(columns, line_number, line_words, type_file)
    if not columns:
        print 'No Columns Found: %s' % loc
        return [], None, None, None

    if type_file == 'generic' or type_file == 'proposed':
        processed = process_generic_page(line_words, drug_start, columns, date)
    elif type_file == 'label':
        processed = process_label_page(line_words, drug_start, columns, date)
    else:
        print 'Wtf? no processed to speak of: %s' % loc
        processed = []

    return processed, date, columns, drug_start, type_file
