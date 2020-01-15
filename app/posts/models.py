from app import db
from datetime import datetime


class Post(db.Model):

    __tablename__ = 'posts'

    post_id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    title = db.Column(db.String(140), nullable=False)
    text = db.Column(db.Text, nullable=False)

    def __init__(self, title, text, user_id):
        self.title = title
        self.text = text
        self.user_id = user_id

    def __repr__(self):
        return f"Post Id: {self.id} --- Date: {self.date} --- Title: {self.title}"


class PlannedFeature(db.Model):

    __tablename__ = 'planned_features'

    feature_id = db.Column(db.Integer, primary_key=True)
    feature_name = db.Column(db.String(64))
    feature_planned_start = db.Column(db.DateTime)
    feature_planned_end = db.Column(db.DateTime)
    feature_fact_start = db.Column(db.DateTime)
    feature_fact_end = db.Column(db.DateTime)
    feature_comment = db.Column(db.String(255))

    def __init__(self, feature_id, feature_name, feature_planned_start, feature_planned_end,
                 feature_fact_start, feature_fact_end, feature_comment):
        self.feature_id = feature_id
        self.feature_name = feature_name
        self.feature_planned_start = feature_planned_start
        self.feature_planned_end = feature_planned_end
        self.feature_fact_start = feature_fact_start
        self.feature_fact_end = feature_fact_end
        self.feature_comment = feature_comment

    def __repr__(self):
        return str(self.feature_id) + ": " + str(self.feature_name)


class Voting(db.Model):

    __tablename__ = 'votings'

    voting_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    active = db.Column(db.Integer, default=True)

    def __init__(self, title, description, user_id):
        self.title = title
        self.description = description
        self.user_id = user_id

    def __repr__(self):
        return str(self.title)


class VotingOption(db.Model):

    __tablename__ = 'voting_options'

    voting_option_id = db.Column(db.Integer, primary_key=True)
    voting_id = db.Column(db.Integer, db.ForeignKey('votings.voting_id'))
    title = db.Column(db.String(255))
    text = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, title, text, user_id, voting_id):
        self.title = title
        self.text = text
        self.user_id = user_id
        self.voting_id = voting_id

    def __repr__(self):
        return str(self.title)


class Vote(db.Model):

    __tablename__ = 'votes'

    vote_id = db.Column(db.Integer, primary_key=True)
    voting_option_id = db.Column(db.Integer, db.ForeignKey('voting_options.voting_option_id'))
    vote_value = db.Column(db.String(255))
    value_type = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, vote_value, value_type, user_id):
        self.vote_value = vote_value
        self.value_type = value_type
        self.user_id = user_id

    def __repr__(self):
        return str(self.user_id) + ": " + str(self.voting_option_id) + ": " + str(self.vote_value)
