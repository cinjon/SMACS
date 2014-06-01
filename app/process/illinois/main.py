import app
import os

########
# Illinois's main.py: Guides the IL processing
#
# Central function is def process(...)
########

parent_directory = os.path.dirname(os.path.realpath(__file__))
documents = parent_directory + '/documents'
header_max_lines = 10

def process(loc, date=None, columns=None, type_file=None):
    # Runs the processing for IL
    # loc is a file location
    # date is a datetime object, passed in to the later html files in an hocr dir after processing the first
    # columns is a list of columns, similarly processed by the first and passed to the rest
    # type_file is string:{proposed, generic, label}

    line_words = app.process.load.get_all_line_words(loc)

    # It isn't reliable to depend on later pages having the same drug_start as earlier ones
    drug_start = get_drug_start(line_words)

    if not type_file:
        type_file = get_type_of_file(loc, line_words, drug_start)

    date = get_date_from_header(date, line_words)
    if not date:
        print 'No date in %s' % loc
        return [], None, None, None

    columns = get_columns_from_file(columns, line_words, type_file)
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

    return processed, date, columns, type_file

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
                if '.' in txt and not any([month in txts for month in app.process.utility.months]):
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

def get_date_from_header(date, line_words):
    # If not date, finds and returns the date in the header
    if date:
        return date
    for index in range(header_max_lines):
        date = app.process.utility.datetime_from_regex(
            ' '.join([word.txt for word in line_words[index]]))
        if date:
            return date
    return None

def state_specific_linefix_funcs():
    def fix_line_conversion_mistakes(line, prev_line, next_line):
        line_text = ' '.join([w.txt for w in line])
        if line_text == 'L b I N G _ N Old SMAC Current SMAC':
            label_word = app.models.Word('Label Name',
                                         line[0].l, line[0].t, line[3].r, next_line[0].b)
            generic_word = app.models.Word('Generic Name',
                                           line[4].l, line[4].t, line[6].r, next_line[0].b)
            temp = line[7:]
            line = [label_word, generic_word]
            line.extend(temp)
        return line
    return [fix_line_conversion_mistakes]

def state_specific_wordfix_funcs():
    column_text_dict = {'Generic_Name':'Generic Name', 'Wren':'Current'}

    def fix_word_zeros(word):
        word.txt = word.txt.replace('0', 'O')
        return word
    def fix_word_column_names(word):
        txt = word.txt
        if txt in ['N', 't']:
            #Notes ... skipping for now
            word.txt = None
        elif txt in column_text_dict:
            word.txt = column_text_dict[txt]
        elif txt.replace('_', '') in column_text_dict:
            word.txt = column_text_dict[txt.replace('_', '')]
        return word
    return [fix_word_zeros, fix_word_column_names]

def get_columns_from_file(columns, line_words, type_file):
    # If not columns, finds and returns the file's columns
    if columns:
        return columns

    def line_has_columns(line_word_texts):
        # last clause below is because some of the specialty pages convert very poorly
        return 'Generic_Name' in line_text or ('Generic' in line_text and 'Name' in line_text) or ('L' in line_text and 'b' in line_text and 'G' in line_text)

    for index in range(header_max_lines):
        if line_has_columns([w.txt for w in line_words[index]]):
            column_boxes = get_column_bounding_boxes(
                line[index], line_words[index-1], line_words[index+1],
                state_specific_linefix_funcs(), state_specific_wordfix_funcs())
            return merge_column_names(column_boxes, line_words[index+1], type_file)
    return None

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
    # Merge the column names to form the right ones. Highly state dependent
    # and_group_rules is (column.title, next_column.title):(new_column_title, position_delta)
    and_group_rules = {('Generic', 'Name'):('Generic Name', 1), ('Old', 'Smac'):('Old Smac', 1),
                       ('Label', 'Name'):('Label Name', 1), ('Current', 'FUL'):('FUL', 1),
                       ('Current.', 'FUL'):('FUL', 1), ('Current', None):('SMAC', 0),
                       ('Current.', None):('SMAC', 0), ('Cgrint', 'CuSrl:ne:(t:lL'):('FUL', 0),
                       ('CuSrl:ne:(t:lL', 'SMAC'):('SMAC', 0), ('Current SMAC', None):('SMAC', 0)}

    def get_title_and_delta_from_and_rules(column, next_column):
        for group, result in and_group_dict.iteritems():
            if column.title == group[0] and (not groups[1] or next_column.title == groups[1]):
                return result[0], result[1]
        return None, None
    def get_title_from_prev_column(column, next_column, prev_title, next_line)
        if column.title == 'SMAC' and next_column.title == 'Notes':
            has_collision, text = app.process.utility.has_colliding_column(column, next_line)
            if has_collision:
                return column.title + ' ' + text, 0
            elif prev_title == 'Current':
                return 'Effective Date', 0
            elif prev_title == 'Current SMAC' or prev_title == 'SMAC': #column changed from CuSrl..
                return 'Proposed SMAC', 0
        else:
            return column.title, 0

    ret = []
    for position in range(len(columns)):
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
        title, position_delta = get_title_and_delta_from_and_rules(column, next_column)
        if not title:
            title = get_title_from_prev_column(column, next_column, prev_title, next_line)
            position_delta = 0

        position += position_delta
        if position_delta > 0:
            new_column = app.models.Column(title, column.l, min(column.t, next_column.t),
                                           next_column.r, max(column.b, next_column.b))
            ret.append(new_column)
        else:
            column.title = title
            ret.append(column)

    if len(next_line) == 1 and next_line[0].txt == 'Proposed' and next_line[0].l > columns[-1].r:
        col = next_line[0]
        ret.append(app.models.Column('Proposed SMAC', col.l, col.t, col.r, col.b))
    return ret

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
