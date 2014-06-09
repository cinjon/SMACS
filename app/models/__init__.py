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

class CanonicalNames(app.db.Model):
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
