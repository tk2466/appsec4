from flask_login import UserMixin

from app import *


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    phonenumber = db.Column(db.String(11), nullable=False)
    role = db.Column(db.String())
    spelling_history = db.relationship('Spelling_History', backref='checker', lazy=True)
    session = db.relationship('Session', backref='checker', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.role}')"


class Spelling_History(db.Model):
    __tablename__ = "spelling_history"
    id = db.Column(db.Integer, primary_key=True)
    query_text = db.Column(db.String(), nullable=False)
    query_result = db.Column(db.String(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Spelling_History('{self.query_text}', '{self.query_result}')"


class Session(db.Model):
    __tablename__ = "session"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, nullable=False)
    logout = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Session('{self.login}', '{self.logout}')"

