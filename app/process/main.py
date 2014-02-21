import app

def get_assignment_float(d, key):
    value = d.get(key)
    if value:
        return float(value)
    return None

def process_to_db(directory):
    assignments, date = app.process.illinois.main.process_hocr_dir(directory + '/hocr/')
    date = app.utility.datetime_from_legible(date)
    for assignment in assignments:
        generic_name = assignment.get('Generic Name')
        if not generic_name:
            print 'No Generic Name: %s' % assignment
            continue

        drug = app.models.Drug.query.filter(app.models.Drug.generic_name == generic_name).first() #should be just 1
        if not drug:
            drug = app.models.Drug(generic_name, assignment.get('Strength'),
                                   assignment.get('Form'), assignment.get('Label Name'))
            app.db.session.add(drug)

        listing = app.models.Listing(effective_date=date,
                                     smac=get_assignment_float(assignment, 'Current'),
                                     ful=get_assignment_float(assignment, 'FUL'),
                                     state='IL', drug_id=drug.id)
        drug.listings.append(listing)
        app.db.session.add(listing)
        app.db.session.commit()


