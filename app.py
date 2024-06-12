from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask_marshmallow import Marshmallow
from marshmallow.validate import Length
from flask_bcrypt import Bcrypt

# pylint: disable=E1101
app = Flask(__name__)


## DB CONNECTION AREA
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql+psycopg2://tomato:123456@localhost:5432/ripe_tomatoes_db"
)
db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)



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
            first_name="Morgan",
            last_name="Freeman",
            gender="Male",
            country="USA",
            date_of_birth="1 June 1937",
        ),
        Actor(
            first_name="Anthony",
            last_name="Hopkins",
            gender="Male",
            country="UK",
            date_of_birth="31 December 1937",
        ),
        Actor(
            first_name="Nathan",
            last_name="Fillion",
            gender="Male",
            country="Canada",
            date_of_birth="27 March 1971",
        ),
        Actor(
            first_name="Abigail",
            last_name="Spencer",
            gender="Female",
            country="USA",
            date_of_birth="4 August 1971",
        ),
    ]
    # Users Object
    users = [
            User(
            email = "admin",
            password = bcrypt.generate_password_hash("password123").decode('utf-8'),
            admin = True
            ),
            User(
            email = "user1",
            password = bcrypt.generate_password_hash("12345678").decode('utf-8')
            ),
    ]

    db.session.add_all(movies)
    db.session.add_all(actors)
    db.session.add_all(users)
    db.session.commit()
    print("Movies added")
    print("Actors added")
    print("users added")


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
    country = db.Column(db.String(50))
    date_of_birth = db.Column(db.Text())


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    admin = db.Column(db.Boolean(), default=False)


# SCHEMAS AREA


class movieSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "genre", "length", "release_year", "rating")


class actorSchema(ma.Schema):
    class Meta:
        fields = ("id", "first_name", "last_name", "gender", "country", "date_of_birth")


class userSchema(ma.Schema):
    class Meta:
        model = User
        fields = ("email", "password", "admin")
        # set the password's length to a minimum of 6 characters
        password = ma.String(validate=Length(min=8))

user_schema = userSchema()
users_schema = userSchema(many=True)


# ROUTING AREA


@app.route("/")
def hello():
    return "Welcome to Ripe Tomatoes API"


@app.route("/movies")
def all_movies():
    stmt = db.Select(Movie)
    movies = db.session.scalars(stmt).all()
    return movieSchema(many=True).dump(movies)


@app.route("/actors")
def all_actors():
    stmt = db.Select(Actor)
    actors = db.session.scalars(stmt).all()
    return actorSchema(many=True).dump(actors)

@app.route('/auth/signup', methods=["POST"])
def auth_register():
    #The request data will be loaded in a user_schema converted to JSON. request needs to be imported from
    user_fields = user_schema.load(request.json)
    #Create the user object
    user = User()
    #Add the email attribute
    user.email = user_fields['email']
    #Add the password attribute hashed by bcrypt
    user.password = bcrypt.generate_password_hash(user_fields['password']).decode('utf-8')
    #Add it to the database and commit the changes
    db.session.add(user)
    db.session.commit()
    #Return the user to check the request was successful
    return jsonify(user_schema.dump(user))


