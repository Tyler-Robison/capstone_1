from flask.helpers import flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import backref
from werkzeug.utils import redirect



db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    db.app = app
    db.init_app(app)


class User(db.Model):
    """User model"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False, unique=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    # start_register
    @classmethod
    def register(cls, username, password, email, first_name, last_name, is_admin):
        """Register User with hashed password and return user"""

        hashed = bcrypt.generate_password_hash(password)

        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, password=hashed_utf8, first_name=first_name, last_name=last_name, email=email, is_admin=is_admin)
    # end_register

    # start_authenticate
    @classmethod
    def authenticate(cls, username, pwd):
        """Checks that username exists and password is correct"""

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, pwd):
            return user
        else:
            return False
    # end_authenticate