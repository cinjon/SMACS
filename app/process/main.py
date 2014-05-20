import app
import os
import traceback
import urllib2
import shutil
import urlparse

def get_directory_from_state(state):
    directory = None
    if state == 'IL':
        directory = app.process.illinois.main.documents
    return directory

def get_process_function_from_state(state):
    process = None
    if state == 'IL':
        process = app.process.illinois.main.process
    return process

def is_done_dir(f):
    dir_name = f.split('/')[-1]
    return dir_name == '' or dir_name == 'done' or '/done' in f  #top-level || done docs

def download_files_from_state(state):
    if state == 'IL':
        app.process.illinois.load.download_files()

def do_all_processing_for_state(state):
    try:
        print 'Downloading files from ' + state
        download_files_from_state(state)
        print 'Completed downloading files from ' + state
        process_from_src_to_hocr(state)
        print 'Completed downloading files from ' + state
        failed, no_generics = process_to_db(state)
        print 'Completed processing to DB for ' + state
        print '*** Failed Listings ***'
        print failed
        print '*** Listings with no generics ***'
        print no_generics
        print 'Moving files to /hocr/done'
        done_hocr(state)
        print 'Done'
    except Exception, e:
        print e

#####
# Call this with the directory path to take src pdf's to hocr's.
#####
def process_from_src_to_hocr(state):
    directory = get_directory_from_state(state)

    #assumes directory has:
    #/src with pdfs to process, /decrypted, /png, /hocr
    src = directory + '/src/'
    decrypted = directory + '/decrypted/'
    png = directory + '/png/'
    hocr = directory + '/hocr/'

    for f in os.listdir(src):
        if f == 'done' or f == '.DS_Store':
            continue
        print 'Starting: %s' % f
        print 'Decrypting'
        app.process.ocr.decrypt_pdf(src, decrypted, f)
        app.process.ocr.done_file(src, f)

        print 'Ghostscripting'
        app.process.ocr.ghostscript_pdf_to_png(decrypted, png, f)
        app.process.ocr.done_file(decrypted, f)

        print 'Tesseracting'
        for png_f in os.listdir(png):
            app.process.ocr.tesseract_png_to_hocr(png, hocr, png_f)
            app.process.ocr.done_file(png, png_f)

def process_from_hocr(state):
    directory = get_directory_from_state(state)
    _process = get_process_function_from_state(state)
    if not directory or not _process:
        return

    directory += '/hocr/'
    master_assignments = {}
    for root, dirs, files in os.walk(directory): #each dir is a diff pdf
        if is_done_dir(root):
            continue
        date = None
        columns = None
        drug_start = None
        type_file = None
        assignments = []
        print root
        for num, f in enumerate(files): #this is bad because the file order is wack. be careful
            if f == '.DS_Store' or f == 'done':
                continue
            absolute_path = root + '/' + f
            try:
                page_assignments, date, columns, drug_start, type_file = _process(absolute_path, date, columns, drug_start, type_file)
                if num == 0:
                    drug_start = None
            except Exception, e:
                print 'Error: %s, ds: %s' % (absolute_path, drug_start)
                traceback.print_exc()

                break
            if not date:
                print 'No Date Found: %s' % absolute_path
            assignments.extend(page_assignments)
            # app.process.ocr.done_file(root + '/', f)
        master_assignments[root] = assignments
    return master_assignments

def done_hocr(state):
    directory = get_directory_from_state(state) + '/hocr/'
    for root, dirs, files in os.walk(directory):
        if is_done_dir(root):
            continue
        app.process.ocr.done_file(directory, root.split('/')[-1])

def get_float_of_value(d, key):
    value = d.get(key)
    if value:
        return float(value)
    return None

def _process_to_db(file_assignments, state):
    failed_listings = {}
    no_generics = {}
    for f, assignments in file_assignments.iteritems():
        print f
        seen_generic_names = {}
        seen_label_names = {}
        for assignment in assignments:
            generic_name = assignment.get('Generic Name')
            if not generic_name:
                print 'No Generic Name for assignment'
                print assignment
                if f not in no_generics:
                    no_generics[f] = []
                no_generics[f].append(assignment)
                continue

            label_name = assignment.get('Label Name')
            if label_name:
                seen_assignments = seen_label_names.get(label_name, [])
                if any([seen_assignment.get('Generic Name') == generic_name for seen_assignment in seen_assignments]):
                    print 'Label Name %s seen already with Generic: %s' % (label_name, generic_name)
                    continue
                seen_assignments.append(assignment)
                seen_label_names[label_name] = seen_assignments
            else:
                if generic_name in seen_generic_names:
                    print '%s seen already' % generic_name
                    continue
                seen_generic_names[generic_name] = assignment

            drug = app.models.Drug.query.filter(
                app.models.Drug.generic_name == generic_name,
                app.models.Drug.label_name == label_name).first() #should be just 1
            if not drug: #make drug
                drug = app.models.Drug(
                    generic_name, assignment.get('Strength'),
                    assignment.get('Form'), label_name)
                app.db.session.add(drug)

            try:
                listing = app.models.Listing(
                    effective_date=assignment.get('Date'),
                    smac=get_float_of_value(assignment, 'SMAC'),
                    ful=get_float_of_value(assignment, 'FUL'),
                    proposed=get_float_of_value(assignment, 'Proposed SMAC'),
                    file_found=f.split('/')[-1],
                    state=state,
                    drug_id=drug.id)
            except Exception, e:
                print 'Listing failed'
                print assignment
                if f not in failed_listings:
                    failed_listings[f] = []
                failed_listings[f].append(assignment)
                continue
            drug.listings.append(listing)
            app.db.session.add(listing)
            app.db.session.commit()
    return failed_listings, no_generics

def process_to_db(state):
    if not state:
        print "Yo, where the fuck's your state?"
        return

    file_assignments = process_from_hocr(state)
    if not file_assignments or len(file_assignments) == 0:
        print "Assignments didn't work"
        return

    return _process_to_db(file_assignments, state)

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
