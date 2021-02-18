from datetime import datetime
from flask import current_app
from flask_login import UserMixin
from itsdangerous import (JSONWebSignatureSerializer as Serializer, TimedJSONWebSignatureSerializer as TimedSerializer)

from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(9999), unique=True, nullable=False)
    password = db.Column(db.String(9999), nullable=False)
    activated = db.Column(db.Boolean(), nullable=False, default=False)
    managed_links = db.relationship('Link', backref='user', lazy='dynamic')

    def get_activation_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id, 'email': self.email}).decode('utf-8')

    @staticmethod
    def verify_activation_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        email = s.loads(token)['email']
        return User.query.get(user_id), email

    def get_reset_token(self, expires_seconds=1800):
        s = TimedSerializer(current_app.config['SECRET_KEY'], expires_seconds)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = TimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.id}', '{self.email}')"


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(9999), nullable=False)
    original_url = db.Column(db.String(9999), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    clicks = db.relationship('Click', backref='link', lazy='dynamic')

    def __repr__(self):
        return f"Link('{self.id}, {self.link}', '{self.original_url}', '{self.date_created}', '{self.user_id}')"


class Click(db.Model):
    click_id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('link.id'), nullable=False)
    date_clicked = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ip_address = db.Column(db.String(20), nullable=True)
    user_agent = db.Column(db.String(9999), nullable=True)
    referrer_page = db.Column(db.String(99999), nullable=True)

    def __repr__(self):
        return f"Click('{self.link_id}, {self.time}, {self.ip_address}, {self.user_agent}, {self.referrer_page}"
