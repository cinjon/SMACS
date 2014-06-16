import app
# from flask.ext.security import UserMixin, RoleMixin
# from flask.ext.security.utils import verify_and_update_password

ROLE_USER = 0
ROLE_ADMIN = 1
ROLE_TEST = 2

# roles_users = app.db.Table(
#     'roles_users',
#     app.db.Column('smac_user_id', app.db.Integer(), app.db.ForeignKey('smac_user.id')),
#     app.db.Column('role_id', app.db.Integer(), app.db.ForeignKey('role.id')))

drugs = app.db.Table(
    'company_drugs',
    app.db.Column('drug_id', app.db.Integer, app.db.ForeignKey('drug.id')),
    app.db.Column('company_id', app.db.Integer, app.db.ForeignKey('company.id'))
)

# class Role(app.db.Model, RoleMixin):
#     id = app.db.Column(db.Integer(), primary_key=True)
#     name = app.db.Column(db.String(80), unique=True)
#     description = app.db.Column(db.String(255))

# class SmacUser(app.db.Model, UserMixin):
#     id = app.db.Column(app.db.Integer, primary_key=True)
#     contact_name = app.db.Column(app.db.String(120))
#     email = app.db.Column(app.db.String(120), unique=True, index=True) #Required
#     password = app.db.Column(app.db.String(120)) #Required
#     active = app.db.Column(app.db.Boolean())
#     creation_time = app.db.Column(app.db.DateTime)
#     last_login_at = app.db.Column(app.db.DateTime())
#     current_login_at = app.db.Column(app.db.DateTime())
#     last_login_ip = app.db.Column(app.db.String(100))
#     current_login_ip = app.db.Column(app.db.String(100))
#     login_count = app.db.Column(app.db.Integer)
#     confirmed_at = app.db.Column(app.db.DateTime())
#     roles = app.db.relationship('Role', secondary=roles_users,
#                                 backref=app.db.backref('users', lazy='dynamic'))

#     def __init__(self, contact_name, email, password, roles, active):
#         self.email = email
#         self.contact_name = contact_name
#         self.active = active
#         self.password = password
#         self.creation_time = app.utility.get_time()
#         self.roles = roles

#     def is_authenticated(self):
#         #Can the user be logged in in general?
#         return True

#     def is_active(self):
#         #Is this an active account or perhaps banned?
#         return True

#     def is_anonymous(self):
#         return False

#     def get_id(self):
#         return unicode(self.id)

#     def check_password(self, password):
#         return verify_and_update_password(password, self)

def try_login(email, password, remember_me=True, xhr=False):
    u = user_with_email(email)
    if u and authenticate(u, password):
        session.pop('remember_me', None)
        login_user(u, remember=remember_me)
        if xhr:
            return app.utility.xhr_user_login(u, True)
    elif xhr:
        return app.utility.xhr_user_login(u, False)
    return app.views.index.go_to_index()

def authenticate(u, password):
    return u.check_password(password)

class Drug(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    creation_time = app.db.Column(app.db.DateTime)
    label_name = app.db.Column(app.db.Text(), index=True)
    generic_name = app.db.Column(app.db.Text(), index=True)
    unique_id = app.db.Column(app.db.String(12), unique=True)
    companies = app.db.relationship('Company', secondary=drugs,
                                    backref=app.db.backref('drugs', lazy='dynamic'))
    listings = app.db.relationship('Listing', lazy='dynamic', backref='drug')
    edited = app.db.Column(app.db.Boolean, index=True)

    def __init__(self, generic_name, label_name):
        self.generic_name = generic_name
        self.label_name = label_name
        self.unique_id = app.utility.generate_id()
        self.creation_time = app.utility.get_time()
        self.edited = False

    def __dir__(self):
        return ['creation_time', 'label_name', 'id', 'generic_name',
                'companies', 'listings', 'edited', 'unique_id']

    def create_canonical_generic_match(self, canonical_name, strength, form):
        generic_name_as_key = self.generic_name
        self.generic_name = canonical_name
        app.models.create_canonical_name(generic_name_as_key, canonical_name, strength, form)

    def create_canonical_label_match(self, canonical_name, strength, form):
        label_name_as_key = self.label_name
        self.label_name = canonical_name
        app.models.create_canonical_name(label_name_as_key, canonical_name, strength, form)

    def set_listing_attributes(self, strength, form):
        for listing in self.listings:
            listing.strength = strength
            listing.form = form
        app.db.session.commit()

def create_drug(generic_name, label_name):
    drug = app.models.Drug(generic_name, label_name)
    app.db.session.add(drug)
    return drug

def get_or_create_drug(generic_name, label_name):
    # Drug is given by generic_name and label_name, possible None for either
    drug = app.models.Drug.query.filter(app.models.Drug.generic_name == generic_name,
                                        app.models.Drug.label_name == label_name).first()
    return drug or create_drug(generic_name, label_name)

class Listing(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    creation_time = app.db.Column(app.db.DateTime)
    strength = app.db.Column(app.db.String(25))
    form = app.db.Column(app.db.String(25))
    drug_id = app.db.Column(app.db.Integer, app.db.ForeignKey('drug.id'), index=True)
    ful = app.db.Column(app.db.Float)
    smac = app.db.Column(app.db.Float)
    proposed = app.db.Column(app.db.Float)
    state = app.db.Column(app.db.String(2), index=True)
    effective_date = app.db.Column(app.db.DateTime, index=True)
    file_found = app.db.Column(app.db.Text())
    price_checked = app.db.Column(app.db.Boolean, index=True)

    def __init__(self, strength, form, smac, effective_date, proposed, state, drug_id, ful, file_found):
        self.strength = strength
        self.form = form
        self.smac = smac
        self.effective_date = effective_date
        self.drug_id = drug_id
        self.ful = ful
        self.state = state
        self.proposed = proposed
        self.file_found = file_found
        self.creation_time = app.utility.get_time()
        self.price_checked = False

    def __dir__(self):
        return ['effective_date', 'form', 'ful', 'file_found',
                'smac', 'state', 'strength', 'proposed']

class CanonicalNames(app.db.Model):
    #This should be CanonicalName*****
    id = app.db.Column(app.db.Integer, primary_key=True)
    name_as_key = app.db.Column(app.db.Text(), index=True, unique=True)
    canonical_name = app.db.Column(app.db.Text())
    strength = app.db.Column(app.db.String(25))
    form = app.db.Column(app.db.String(25))

    def __init__(self, name_as_key, canonical_name, strength, form):
        self.name_as_key = name_as_key
        self.canonical_name = canonical_name
        self.strength = strength
        self.form = form

def set_canonical_generic_name(drug, canonical_name, strength, form):
    # Looks to see if another drug has the same generic_name as this canonical_name
    # Merge the two drugs by moving these listings to that one and deletes this one
    # If no match, sets this one to be the new name
    # Either way, tables this (generic_name, canonical_name, strength, form) quad

    try:
        response = {}
        existing_drug = app.models.Drug.query.filter(app.models.Drug.generic_name == canonical_name, app.models.Drug.label_name == None).first() # There should only be one other if that
        drug.create_canonical_generic_match(canonical_name, strength, form)
        if existing_drug:
            # We found another. Merge these together
            existing_drug.companies.extend([c for c in drug.companies])
            existing_drug.listings.extend([l for l in drug.listings])
            app.db.session.delete(drug)
            response['deleted'] = True
        app.db.session.commit()
        response['success'] = True
        response['generic_name'] = canonical_name
        return response
    except Exception, e:
        print e
        app.db.session.rollback()
        return {'success':False}

def set_canonical_label_name(drug, canonical_label_name, canonical_generic_name, strength, form):
    # Looks to see if something else has this canonical_name
    # If so, merges the drugs by moving these listings to that one and deletes this one

    try:
        response = {}
        # There should only be one match if that
        existing_drug = app.models.Drug.query.filter(
            app.models.Drug.generic_name == canonical_generic_name,
            app.models.Drug.label_name == canonical_label_name).first()
        drug.create_canonical_generic_match(canonical_generic_name, strength, form)
        drug.create_canonical_label_match(canonical_label_name, strength, form)

        if existing_drug:
            # We found another. Merge these together
            existing_drug.companies.extend([c for c in drug.companies])
            existing_drug.listings.extend([l for l in drug.listings])
            app.db.session.delete(drug)
            response['deleted'] = True
        app.db.session.commit()
        response['success'] = True
        response['generic_name'] = canonical_generic_name
        response['label_name'] = canonical_label_name
        return response
    except Exception, e:
        print e
        app.db.session.rollback()
        return {'success':False}

def create_canonical_name(name_as_key, canonical_name, strength, form):
    name = app.models.CanonicalNames(
        name_as_key, canonical_name, strength, form)
    app.db.session.add(name)
    return name

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
