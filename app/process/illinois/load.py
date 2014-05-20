import app
import urllib2
from BeautifulSoup import BeautifulSoup

baseurl = 'http://www.ilsmac.com/list/files/'

do_specialty = True
def _check_specialty(href):
    if do_specialty:
        return True
    else:
        return 'specialty' not in href

def _only_specialty(href):
    return 'specialty' in href

def files_later_than(date, file_ends):
    ret = []
    seen = set()
    for file_end in file_ends:
        if file_end in seen:
            continue
        seen.add(file_end)

        file_date = app.utility.datetime_from_regex(file_end)
        if not file_date:
            print 'whats up with this file_end? it has no date: %s' % file_end
        elif not date or file_date > date:
            ret.append(file_end)
        else: #done.
            break
    return ret

def _get_urls(date):
    #returns all urls from illinois smac site after the given date
    url = 'http://www.ilsmac.com/list'
    f = urllib2.urlopen(urllib2.Request(url))
    soup = BeautifulSoup(f)
    a_types = soup.findAll('a')

    all_file_ends = [a.get('href').split('/')[-1] for a in a_types if '/list/files' in a.get('href', '') and _only_specialty(a.get('href', ''))]
    return [baseurl + f for f in files_later_than(date, all_file_ends)]

def _get_latest_date():
    #get the date from the db
    from sqlalchemy import func
    listing = app.models.Listing
    most_recent_date = app.db.session.query(func.max(listing.effective_date)).filter(listing.state=='IL', listing.proposed != None).all()[0][0]
    if most_recent_date:
        return most_recent_date.date()
    return None

def download_files(debug=False):
    date = _get_latest_date()
    urls = _get_urls(date)
    if debug:
        return urls
    for url in urls:
        app.process.main.download(url, app.process.illinois.main.documents + '/src')
