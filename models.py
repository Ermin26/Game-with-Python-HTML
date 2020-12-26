import os
from sqla_wrapper import SQLAlchemy

db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///users.sqlite"))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String,)
    session_token = db.Column(db.String,)
    secret_number = db.Column(db.Integer, unique=False)
    games = db.Column(db.Integer,)
    wins = db.Column(db.Integer,)
    losses = db.Column(db.Integer,)
    pl_games = db.Column(db.Integer,)
    pl_wins = db.Column(db.Integer,)
    pl_losses = db.Column(db.Integer,)

""""
class ScoreList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    pl_games = db.Column(db.Integer,)
    pl_wins = db.Column(db.Integer,)
    pl_losses = db.Column(db.Integer,)"""
