import peewee as db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import login
from local_params import *

database = db.MySQLDatabase(DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=3306)


@login.user_loader
def load_user(id):
    try:
        return User.get_by_id(id)
    except db.DoesNotExist:
        return None


class Model(db.Model):
    class Meta:
        database = database


class User(UserMixin, Model):
    username = db.CharField(unique=True)
    password = db.CharField()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Contact(Model):
    from_person = db.ForeignKeyField(User)
    to_person = db.ForeignKeyField(User)
