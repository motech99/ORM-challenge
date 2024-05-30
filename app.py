from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask_marshmallow import Marshmallow

app = Flask(__name__)






## DB CONNECTION AREA
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql+psycopg2://tomato:123456@localhost:5432/ripe_tomatoes_db"
)
db = SQLAlchemy(app)
ma = Marshmallow(app)


# CLI COMMANDS AREA

# MODELS AREA
class Movie(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.Text())
    genre = db.Column(db.String(100))
    length = db.Column(db.Integer)
    release_year = db.Column(db.Integer)

class Actor(db.Model):
    __tablename__='actors'

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    gender = db.Column(db.String(20))
    date_of_birth = db.Column(db.Text())






# SCHEMAS AREA

# ROUTING AREA


@app.route("/")
def hello():
    return "Welcome to Ripe Tomatoes API"
