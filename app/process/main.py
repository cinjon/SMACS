import app
import os

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
        if f == 'done':
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
    assignments = []
    for root, dirs, files in os.walk(directory): #each dir is a diff pdf
        dir_name = root.split('/')[-1]
        if dir_name == '' or dir_name == 'done': #top-level || done docs
            continue
        date = None
        cols = None
        title = None
        for f in files:
            page_assignments, date, cols, title = _process(
                root + '/' + f, date, cols, title)
            assignments.extend(page_assignments)
            # app.process.ocr.done_file(root + '/', f)
    return assignments

def get_float_of_value(d, key):
    value = d.get(key)
    if value:
        return float(value)
    return None

def process_to_db(state):
    if not state:
        print "Yo, where the fuck's your state?"
        return
    elif state == 'IL':
        assignments = app.process.illinois.main.process_hocr_dir()

    for assignment in assignments:
        generic_name = assignment.get('Generic Name')
        if not generic_name:
            continue

        drug = app.models.Drug.query.filter(
            app.models.Drug.generic_name == generic_name).first() #should be just 1
        if not drug: #make drug
            drug = app.models.Drug(
                generic_name, assignment.get('Strength'),
                assignment.get('Form'), assignment.get('Label Name'))
            app.db.session.add(drug)

        listing = app.models.Listing(
            effective_date=assignment.get('Date'),
            smac=get_float_of_value(assignment, 'Current'),
            ful=get_float_of_value(assignment, 'FUL'),
            state='IL', drug_id=drug.id)
        drug.listings.append(listing)
        app.db.session.add(listing)
        app.db.session.commit()
