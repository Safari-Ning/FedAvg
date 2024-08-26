# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
from sqlalchemy import Binary, Column, Integer, String

from app import db, login_manager

from app.base.util import hash_pass

class User(db.Model, UserMixin):

    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(Binary)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass( value ) # we need bytes here (not plain str)
                
            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    return user if user else None


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer,primary_key=True,autoincrement=True,nullable=False)

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            return False

class Task(BaseModel):
    __tablename__ = "task"
    gpu = db.Column(db.Integer,nullable=False)
    num_of_clients = db.Column(db.Integer,nullable=False)
    cfraction = db.Column(db.Float,nullable=False)
    epoch = db.Column(db.Integer,nullable=False)
    batchsize = db.Column(db.Integer,nullable=False)
    modelname = db.Column(db.String(16),nullable=False)
    learning_rate = db.Column(db.Float,nullable=False)
    val_freq = db.Column(db.Integer,nullable=False)
    save_freq = db.Column(db.Integer,nullable=False)
    num_comm = db.Column(db.Integer,nullable=False)
    save_path = db.Column(db.String(64),nullable=False)
    iid = db.Column(db.Integer,nullable=False)