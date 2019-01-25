import peewee as db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import login
from local_params import *
import json

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


class StreamModel(Model):
    """
    To keep track of running video chats.
    This class is used in recording and merging of chat videos.
    """
    peer1ID = db.ForeignKeyField(model=User)
    peer2ID = db.ForeignKeyField(model=User)
    streamName = db.CharField(unique=True)
    # last stream id which peer 1 has sent
    streamID = db.IntegerField()
    fin = db.BooleanField(default=False)


class ChatVideos(Model):
    """
    Recorded chat videos.
    """
    peer1 = db.ForeignKeyField(model=User)
    peer2 = db.ForeignKeyField(model=User)
    fileAddress = db.CharField()
    chatDate = db.DateTimeField()
