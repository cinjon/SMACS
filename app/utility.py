import datetime
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash

start_date = datetime.datetime(year=1970,month=1,day=1)

def get_time():
    return datetime.datetime.utcnow()

#TODO: turn get_time entries into these.
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
