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


# Drop the tables
@app.cli.command("db_drop")
def db_drop():
    db.drop_all()
    print("Tables have been dropped!")


# Create Tables
@app.cli.command("db_create")
def db_create():
    db.create_all()
    print("Tables have been created!")


@app.cli.command("seed")
def seed_db():

    # Movies object
    movies = [
        Movie(
            title="Megamind",
            genre="Comedy",
            length=95,
            release_year=2010,
            rating="7.3",
        ),
        Movie(
            title="Tron: Legacy",
            genre="Sci-fi",
            length=125,
            release_year=2010,
            rating="6.8",
        ),
        Movie(
            title="Iron Man",
            genre="Action",
            length=126,
            release_year=2008,
            rating="7.9",
        ),
    ]

    # Actors Object
    actors = [
        Actor(
            first_name ='Morgan',
            last_name ='Freeman',
            gender ='Male',
            date_of_birth = '1 June 1937',
            
        ),
        Actor(
            first_name ='Anthony',
            last_name ='Hopkins',
            gender ='Male',
            date_of_birth = '31 December 1937',
        ),
        Actor(
            first_name ='Nathan',
            last_name ='Fillion',
            gender ='Male',
            date_of_birth = '27 March 1971'
        ),
        Actor(
            first_name ='Abigail',
            last_name ='Spencer',
            gender ='Female',
            date_of_birth = '4 August 1971'
        ),
    ]

    db.session.add_all(movies)
    db.session.add_all(actors)
    db.session.commit()
    print('Movies added')
    print('Actors added')


# MODELS AREA
class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.Text())
    genre = db.Column(db.String(50))
    length = db.Column(db.Integer)
    release_year = db.Column(db.Integer)
    rating = db.Column(db.Float)


class Actor(db.Model):
    __tablename__ = "actors"

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
