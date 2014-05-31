import app
import datetime
import subprocess
import urllib2
import shutil
import urlparse

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
