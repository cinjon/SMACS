import app

drugs = app.db.Table(
    'drugs',
    app.db.Column('drug_id', app.db.Integer, app.db.ForeignKey('drug.id')),
    app.db.Column('company_id', app.db.Integer, app.db.ForeignKey('company.id'))
)

class Drug(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    creation_time = app.db.Column(app.db.DateTime)
    label_name = app.db.Column(app.db.Text())
    generic_name = app.db.Column(app.db.Text(), index=True, unique=True)
    strength = app.db.Column(app.db.String(25))
    form = app.db.Column(app.db.String(25))
    companies = app.db.relationship('Company', secondary=drugs,
                                    backref=app.db.backref('drugs', lazy='dynamic'))
    listings = app.db.relationship('Listing', lazy='dynamic', backref='drug')

    def __init__(self, generic_name, strength, form, label_name=None):
        self.generic_name = generic_name
        self.label_name = label_name
        self.strength = strength
        self.form = form
        self.creation_time = app.utility.get_time()

class Listing(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    creation_time = app.db.Column(app.db.DateTime)
    ful = app.db.Column(app.db.Float)
    smac = app.db.Column(app.db.Float)
    state = app.db.Column(app.db.String(2), index=True)
    drug_id = app.db.Column(app.db.Integer, app.db.ForeignKey('drug.id'), index=True)
    effective_date = app.db.Column(app.db.DateTime, index=True)

    def __init__(self, smac, effective_date, state, drug_id, ful=None):
        self.smac = smac
        self.effective_date = effective_date
        self.ful = ful
        self.state = state
        self.drug_id = drug_id
        self.creation_time = app.utility.get_time()

class Company(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    creation_time = app.db.Column(app.db.DateTime)
    name = app.db.Column(app.db.Text(), index=True, unique=True)

    def __init__(self, name):
        self.name = name
        self.creation_time = app.utility.get_time()

class Word(object):
    def __init__(self, text, left, top, right, bottom):
        self.txt = text
        self.l = left
        self.t = top
        self.r = right
        self.b = bottom

#lol-inheritance
class Column(object):
    def __init__(self, title, left, top, right, bottom):
        self.title = title
        self.l = left
        self.t = top
        self.r = right
        self.b = bottom

    def contains(self, word):
        return self.r >= word.l and word.r >= self.l
