from app import db
from datetime import datetime


class LegalEntity(db.Model):

    __tablename__ = 'legal_entities'

    legal_entity_id = db.Column(db.Integer, primary_key=True)
    legal_entity = db.Column(db.String(64))
    legal_entity_short = db.Column(db.String(64))
    legal_entity_group = db.Column(db.String(64))
    legal_entity_short_eng = db.Column(db.String(64))
    legal_entity_code = db.Column(db.String(64))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    access_settings = db.relationship('AccessSetting', backref='legal_entity', lazy=True)

    def __init__(self, legal_entity_id, legal_entity, legal_entity_short,
                 legal_entity_group, legal_entity_short_eng, legal_entity_code):
        self.legal_entity_id = legal_entity_id
        self.legal_entity = legal_entity
        self.legal_entity_short = legal_entity_short
        self.legal_entity_group = legal_entity_group
        self.legal_entity_short_eng = legal_entity_short_eng
        self.legal_entity_code = legal_entity_code

    def __repr__(self):
        return str(self.legal_entity_short_eng)


class Function(db.Model):

    __tablename__ = 'functions'

    function_id = db.Column(db.Integer, primary_key=True)
    function = db.Column(db.String(64))
    description = db.Column(db.String(64))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    cost_centers = db.relationship('CostCenter', backref='function', lazy=True)

    def __init__(self, function_id, function, public_name, description):
        self.function_id = function_id
        self.function = function
        self.public_name = public_name
        self.description = description

    def __repr__(self):
        return str(self.function)


class CostCenter(db.Model):

    __tablename__ = 'cost_centers'

    cost_center_id = db.Column(db.Integer, primary_key=True)
    cost_center = db.Column(db.String(64), unique=True)
    function_id = db.Column(db.Integer, db.ForeignKey('functions.function_id'), nullable=False)
    public_name = db.Column(db.String(256))
    description = db.Column(db.String(256))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    access_settings = db.relationship('AccessSetting', backref='cost_center', lazy=True)

    def __init__(self, cost_center_id, cost_center, function_id, public_name, description):
        self.cost_center_id = cost_center_id
        self.cost_center = cost_center
        self.function_id = function_id
        self.public_name = public_name
        self.description = description

    def __repr__(self):
        return str(self.cost_center)


class Branch(db.Model):

    __tablename__ = 'branches'

    branch_id = db.Column(db.Integer, primary_key=True)
    branch = db.Column(db.String(64), unique=True)
    public_name = db.Column(db.String(64))
    description = db.Column(db.String(128))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    access_settings = db.relationship('AccessSetting', backref='branch', lazy=True)

    def __init__(self, branch_id, branch, public_name, description, date_added):
        self.branch_id = branch_id
        self.branch = branch
        self.public_name = public_name
        self.description = description
        self.date_added = date_added

    def __repr__(self):
        return str(self.branch)


class Location(db.Model):

    __tablename__ = 'locations'

    location_id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(64), unique=True)
    public_name = db.Column(db.String(64))
    description = db.Column(db.String(128))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    access_settings = db.relationship('AccessSetting', backref='location', lazy=True)

    def __init__(self, location_id, location, public_name, description, date_added):
        self.location_id = location_id
        self.location = location
        self.public_name = public_name
        self.description = description
        self.date_added = date_added

    def __repr__(self):
        return str(self.public_name)


class Division(db.Model):

    __tablename__ = 'divisions'

    division_id = db.Column(db.Integer, primary_key=True)
    division = db.Column(db.String(64), unique=True)
    public_name = db.Column(db.String(64))
    description = db.Column(db.String(128))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    access_settings = db.relationship('AccessSetting', backref='division', lazy=True)

    def __init__(self, division_id, division, public_name, description, date_added):
        self.division_id = division_id
        self.division = division
        self.public_name = public_name
        self.description = description
        self.date_added = date_added

    def __repr__(self):
        return str(self.public_name)


class AccessSetting(db.Model):

    __tablename__ = 'access_settings'

    access_setting_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    legal_entity_id = db.Column(db.Integer, db.ForeignKey('legal_entities.legal_entity_id'), nullable=False)
    cost_center_id = db.Column(db.Integer, db.ForeignKey('cost_centers.cost_center_id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.branch_id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.location_id'), nullable=False)
    division_id = db.Column(db.Integer, db.ForeignKey('divisions.division_id'), nullable=False)
    active = db.Column(db.Boolean, default=True)
    date_granted = db.Column(db.DateTime, default=datetime.utcnow)
    date_revoked = db.Column(db.DateTime,  nullable=True)

    users = db.relationship('User', backref='accesses', lazy=True)

    def __init__(self, user_id, legal_entity_id, cost_center_id, branch_id, location_id, division_id):
        self.user_id = user_id
        self.legal_entity_id = legal_entity_id
        self.cost_center_id = cost_center_id
        self.branch_id = branch_id
        self.location_id = location_id
        self.division_id = division_id

    def __repr__(self):
        return str(self.user_id) + ': ' + str(self.cost_center) + ': ' + str(self.location)






