from flask_sqlalchemy import SQLAlchemy
import string
import random

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), nullable=False)
    bookmarks = db.relationship('Bookmark', backref='user')

    def __repr__(self):
        return f'<User {self.username}>'
    

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=False)
    short_url = db.Column(db.String(3), nullable=True)
    visits = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), nullable=False)

    def generate_short_url(self):
        characters = string.digits+string.ascii_letters
        picked_letters = ''.join(random.choices(characters, k=3))

        link = self.query.filter_by(short_url=picked_letters).first()

        # check if it exists in database
        if link:
            self.generate_short_url()
        else:
            return picked_letters

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.short_url = self.generate_short_url()

    def __repr__(self):
        return f'<Bookmark {self.url}>'