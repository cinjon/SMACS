import datetime
import random
import string
import re
import app
from werkzeug.security import generate_password_hash, check_password_hash

start_date = datetime.datetime(year=1970,month=1,day=1)
months = ['january', 'february', 'march', 'april', 'may', 'june', 'july',
          'august', 'september', 'october', 'november', 'december']
abbr_months = ['jan', 'feb', 'march', 'april', 'may', 'june', 'july', 'aug', 'sep', 'oct', 'nov', 'dec']

def get_time():
    return datetime.datetime.utcnow()

def datetime_from_regex(date):
    regexes = app.process.regex

    #These two have the explicit months in them
    match = regexes.legible_date_regex.match(date) or regexes.master_list_date_regex.match(date)
    do_index = True

    if not match:
        #These two have months as numbers
        match = regexes.proposed_date_regex.match(date) or regexes.prop_list_date_regex.match(date)
        do_index = False

    if not match:
        return None

    try:
        groups = match.groups()
        if do_index:
            month = groups[0].replace('0', 'O').lower().strip()
            if month in months:
                month = months.index(month) + 1
            elif month in abbr_months:
                month = abbr_months.index(month) + 1
            else:
                print 'whats up witht his month: %s' % month
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

def get_unixtime(_datetime=None):
    if _datetime:
        return (_datetime - start_date).total_seconds()
    return (datetime.datetime.utcnow() - start_date).total_seconds()

def serialize_datetime(_datetime):
    if _datetime is None:
        return None
    return _datetime.strftime("%Y-%m-%d")

def generate_hash(word):
    return generate_password_hash(word)

def check_hash(stored, request):
    return check_password_hash(stored, request)

def json_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))

def short_text(txt, length, replace):
    if len(txt) > length:
        return txt[:(length - len(replace))]
    return txt

def generate_id(size=6):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(size))

def enum(**enums):
    return type('Enum', (), enums)
