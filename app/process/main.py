import app
import os
import traceback

########
# State specific functions. Call these with the state postal code, e.g. 'IL'
########

def do_all_processing_for_state(state):
    try:
        print 'Downloading files from ' + state
        download_files_from_state(state)
        print 'Completed downloading files for ' + state
        process_from_src_to_hocr(state)
        print 'Completed processing files from src to hocr for ' + state
        failed, no_generics = process_from_hocr_to_db(state)
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

def download_files_from_state(state):
    if state == 'IL':
        app.process.illinois.load.download_files()

def done_hocr(state):
    # So they don't get re-read, moves files from hocr directory to the done directory in hocr.
    directory = get_directory_from_state(state) + '/hocr/'
    for root, dirs, files in os.walk(directory):
        if app.process.utility.is_done_dir(root):
            continue
        app.process.utility.done_file(directory, root.split('/')[-1])

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
        app.process.utility.done_file(src, f)

        print 'Ghostscripting'
        app.process.ocr.ghostscript_pdf_to_png(decrypted, png, f)
        app.process.utility.done_file(decrypted, f)

        print 'Tesseracting'
        for png_f in os.listdir(png):
            app.process.ocr.tesseract_png_to_hocr(png, hocr, png_f)
            app.process.utility.done_file(png, png_f)

def process_from_hocr(state):
    # Processes files in hocr and returns the parsed listings
    directory = get_directory_from_state(state)
    _process = get_process_function_from_state(state)
    if not directory or not _process:
        return

    directory += '/hocr/'
    master_assignments = {}
    for root, dirs, files in os.walk(directory): #each dir is a diff pdf
        if app.process.utility.is_done_dir(root):
            continue
        date = None
        columns = None
        type_file = None
        assignments = []
        print root
        for num, f in enumerate(files): #this is bad because the file order is wack. be careful
            if f == '.DS_Store' or f == 'done':
                continue
            absolute_path = root + '/' + f
            try:
                page_assignments, date, columns, type_file = _process(absolute_path, date, columns, type_file)
            except Exception, e:
                print 'Error: %s' % absolute_path
                traceback.print_exc()

                break
            if not date:
                print 'No Date Found: %s' % absolute_path
            assignments.extend(page_assignments)
        master_assignments[root] = assignments
    return master_assignments

def get_float_of_value(d, key):
    value = d.get(key)
    if value:
        return float(value)
    return None

def _process_from_hocr_to_db(file_assignments, state):
    failed_listings = {}
    no_names = {}
    for f, assignments in file_assignments.iteritems():
        print f
        for assignment in assignments:
            generic_name = assignment.get('Generic Name')
            label_name = assignment.get('Label Name')

            if not generic_name and not label_name:
                if f not in no_names:
                    no_names[f] = []
                no_names[f].append(assignment)
                continue

            drug = app.models.get_or_create_drug(generic_name, label_name)
            try:
                listing = app.models.Listing(
                    effective_date=assignment.get('Date'),
                    smac=get_float_of_value(assignment, 'SMAC'),
                    ful=get_float_of_value(assignment, 'FUL'),
                    proposed=get_float_of_value(assignment, 'Proposed SMAC'),
                    strength=assignment.get('Strength'),
                    form=assignment.get('Form'),
                    file_found=f.split('/')[-1],
                    state=state,
                    drug_id=drug.id)
            except Exception, e:
                if f not in failed_listings:
                    failed_listings[f] = []
                failed_listings[f].append(assignment)
                continue
            drug.listings.append(listing)
            app.db.session.add(listing)
            app.db.session.commit()
    print '%d Failed Listing Creations and %d Listings without Names' % (
        sum([len(k) for k in failed_listings.values()]), sum([len(k) for k in no_names.values()]))
    return failed_listings, no_names

def process_from_hocr_to_db(state):
    file_assignments = process_from_hocr(state)
    if not file_assignments or len(file_assignments) == 0:
        print "No File Assignments. Did you get the state right? --> %s" % state
        return
    return _process_from_hocr_to_db(file_assignments, state)
