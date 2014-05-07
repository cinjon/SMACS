import app
import urllib2
from BeautifulSoup import BeautifulSoup

baseurl = 'http://www.ilsmac.com/list/files/'

do_specialty = False
def _check_specialty(href):
    if do_specialty:
        return True
    else:
        return 'specialty' not in href

def files_later_than(date, file_ends):
    ret = []
    for file_end in file_ends:
        file_date = app.utility.datetime_from_regex(file_end)
        if not file_date:
            print 'whats up with this file_end? it has no date: %s' % file_end
        elif file_date > date:
            print 'yeaaah'
            ret.append(file_end)
        else:
            print 'NNNNoooo'

def _get_urls(date):
    #returns all urls from illinois smac site after the given date
    url = 'http://www.ilsmac.com/list'
    f = urllib2.urlopen(urllib2.Request(url))
    soup = BeautifulSoup(f)
    a_types = soup.findAll('a')

    all_file_ends = [a.get('href').split('/')[-1] for a in a_types if '/list/files' in a.get('href', '') and _check_specialty(a.get('href', ''))]
    return [baseurl + f for f in files_later_than(date, all_file_ends)]

def _get_latest_date():
    #get the date from the db
    from sqlalchemy import func
    listing = app.models.Listing
    most_recent_date = app.db.session.query(func.max(listing.effective_date)).filter(listing.state=='IL').all()[0][0]
    return most_recent_date.date()

def download_files():
    date = _get_latest_date()
    urls = _get_urls(date)
    for url in urls:
        app.process.main.download(url, app.process.illinois.main.documents + '/src')
