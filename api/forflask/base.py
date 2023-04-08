import sqlalchemy 
from flask_sqlalchemy import SQLAlchemy
from api.index import app
from flask_login import UserMixin


db = SQLAlchemy(app=app).Model


# @loginmanager.user_loader
# def Login_user(user_id: str):
#     return User.query.get(user_id)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unigue=True, nullable=False)
    first_name = db.Column(db.String(50), unigue=False, nullable=True)
    last_name = db.Column(db.String(50), unigue=False, nullable=True)

    def __repr__(self):
        return f"<User> {self.username}"


