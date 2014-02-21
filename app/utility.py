import datetime
import random
import string
import re
from werkzeug.security import generate_password_hash, check_password_hash

start_date = datetime.datetime(year=1970,month=1,day=1)
months = ['january', 'february', 'march', 'april', 'may', 'june', 'july',
          'august', 'september', 'october', 'november', 'december']

def get_time():
    return datetime.datetime.utcnow()

legible_date_regex = re.compile("^([a-z]+)\s+(\d+),\s+(\d+)$")
def datetime_from_legible(date):
    # date: January 17, 2013
    ldate = date.lower().strip()
    match = legible_date_regex.match(ldate)
    if not match:
        return None
    try:
        groups = match.groups()
        month = months.index(groups[0]) + 1
        year  = int(groups[2])
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
