import app
import datetime
import subprocess
import urllib2
import shutil
import urlparse

########
# Supporting utility tools for all processing
# Includes functions for state processing
########

########
# Dates
########

months = ['january', 'february', 'march', 'april', 'may', 'june', 'july',
          'august', 'september', 'october', 'november', 'december']
abbr_months = ['jan', 'feb', 'march', 'april', 'may', 'june', 'july', 'aug', 'sep', 'oct', 'nov', 'dec']

def datetime_from_regex(date):
    regexes = app.process.regex

    #These two have the explicit months in them
    match = regexes.legible_date_regex.match(date) or regexes.master_list_date_regex.match(date) or regexes.master_specialty_list_date_regex.match(date)
    do_month_index = True
    if not match:
        #We didn't find a match with the months. Let's look using regex where the months are numbers
        match = regexes.proposed_date_regex.match(date) or regexes.prop_list_date_regex.match(date)
        do_month_index = False

    if not match:
        return None

    try:
        groups = match.groups()
        if do_month_index:
            month = groups[0].replace('0', 'O').lower().strip() #sometimes, that happens using gs
            if month in months:
                month = months.index(month) + 1
            elif month in abbr_months:
                month = abbr_months.index(month) + 1
            else:
                print 'whats up with month: %s' % month
        else:
            month = int(groups[0])
        year  = int(groups[2])
        if year < 2000:
            year += 2000
        day   = int(groups[1])
        return datetime.date(year, month, day)
    except Exception, e:
        print e
        return None

########
# Directory Assistance
########

def is_done_dir(f):
    dir_name = f.split('/')[-1]
    return dir_name == '' or dir_name == 'done' or '/done' in f  #top-level || done docs

def done_file(directory, name):
    done_dir = _check_done_move_for_done(directory, name)
    if not done_dir:
        return
    command = 'mv %s %s' % (directory + name, done_dir + '/' + name)
    subprocess.call(command, shell=True)

def check_done_dir_exists(to_directory, moving_name):
    if moving_name == 'done':
        return False
    done_dir = to_directory + 'done'
    if not os.path.exists(done_dir):
        os.makedirs(done_dir)
    return done_dir

def download(url, dir, fileName=None):
    def getFileName(url,openUrl):
        if 'Content-Disposition' in openUrl.info():
            # If the response has Content-Disposition, try to get filename from it
            cd = dict(map(
                lambda x: x.strip().split('=') if '=' in x else (x.strip(),''),
                openUrl.info()['Content-Disposition'].split(';')))
            if 'filename' in cd:
                filename = cd['filename'].strip("\"'")
                if filename: return filename
                # if no filename was found above, parse it out of the final URL.
        return os.path.basename(urlparse.urlsplit(openUrl.url)[2])

    r = urllib2.urlopen(urllib2.Request(url))
    try:
        fileName = fileName or getFileName(url,r)
        print dir + '/' + fileName
        with open(dir + '/' + fileName, 'wb') as f:
            shutil.copyfileobj(r,f)
    finally:
        r.close()

########
# Bounding Box Utilities
########

def has_colliding_column(column, line):
    for word in line:
        if word.r >= column.l and column.r >= word.l:
            return True, word.txt
    return False, None

def is_missing_column(prev_line_first_word, next_line_last_word, line):
    if prev_line_first_word.r >= next_line_last_word.l and next_line_last_word.r >= prev_line_first_word.l:
        l = min(prev_line_first_word.l, next_line_last_word.l)
        r = max(prev_line_first_word.r, next_line_last_word.r)
        for num, w in enumerate(line):
            if num < len(line)-1 and w.r < l and line[num+1].l > r:
                return True, num
    return False, None

def get_column_bounding_boxes(line, prev_line, next_line,
                              apply_state_specific_line_funcs=[],
                              apply_state_specific_word_funcs=[]):
    # Gets the column bounding boxes given the line where the columns are
    # line is the column line, prev_line and next_line are there for help when conversion is off
    # The state_specific funcs are lists of function rules given by the state's main.py
    columns = []

    for func in apply_state_specific_line_funcs:
        line = func(line, prev_line, next_line)

    for word in line:
        for func in apply_state_specific_word_funcs:
            word = func(word)
        if not word.txt:
            continue
        columns.append(
            app.models.Column(word.txt, int(word.l), int(word.t), int(word.r), int(word.b)))

    prev_line_first_word = prev_line[0]
    next_line_last_word = next_line[-1]
    is_missing, column = is_missing_column(
        prev_line_first_word, next_line_last_word, line)
    if is_missing:
        column += 1
        columns = columns[:column] + [
            app.models.Column(prev_line_first_word.txt + ' ' + next_line_last_word.txt,
                              min(int(prev_line_first_word.l), int(next_line_last_word.l)),
                              int(prev_line_first_word.t),
                              max(int(prev_line_first_word.r), int(next_line_last_word.r)),
                              int(next_line_last_word.b))
            ] + columns[column:]
    return columns
