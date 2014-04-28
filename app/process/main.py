import app
import os
import traceback

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
        dir_name = root.split('/')[-1]
        if dir_name == '' or dir_name == 'done': #top-level || done docs
            continue
        date = None
        columns = None
        drug_start = None
        assignments = []
        print root
        for num, f in enumerate(files): #this is bad because the file order is wack. be careful
            if f == '.DS_Store' or f == 'done':
                continue
            absolute_path = root + '/' + f
            try:
                page_assignments, date, columns, drug_start = _process(absolute_path, date, columns, drug_start)
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

def get_float_of_value(d, key):
    value = d.get(key)
    if value:
        return float(value)
    return None

def _process_to_db(file_assignments, state):
    for f, assignments in file_assignments.iteritems():
        print f
        seen_generic_names = {}
        for assignment in assignments:
            generic_name = assignment.get('Generic Name')
            if not generic_name:
                print 'No Generic Name for assignment'
                print assignment
                continue

            if generic_name in seen_generic_names:
                print '%s seen already' % generic_name
                print seen_generic_names[generic_name]
                print assignment
                continue
            seen_generic_names[generic_name] = assignment

            drug = app.models.Drug.query.filter(
                app.models.Drug.generic_name == generic_name).first() #should be just 1
            if not drug: #make drug
                drug = app.models.Drug(
                    generic_name, assignment.get('Strength'),
                    assignment.get('Form'), assignment.get('Label Name'))
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
                break
            drug.listings.append(listing)
            app.db.session.add(listing)
            app.db.session.commit()
        print '\n'

def process_to_db(state):
    if not state:
        print "Yo, where the fuck's your state?"
        return

    file_assignments = process_from_hocr(state)
    if not file_assignments or len(file_assignments) == 0:
        print "Assignments didn't work"
        return

    _process_to_db(file_assignments, state)
