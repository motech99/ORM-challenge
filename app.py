from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from flask_marshmallow import Marshmallow
from marshmallow.validate import Length
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# pylint: disable=E1101

app = Flask(__name__)


## DB CONNECTION AREA
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql+psycopg2://tomato:123456@localhost:5432/ripe_tomatoes_db"
)
app.config["JWT_SECRET_KEY"] = "Backend best end"


db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


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
            email="admin@email.com",
            password=bcrypt.generate_password_hash("password123").decode("utf-8"),
            admin=True,
        ),
        User(
            email="user1@email.com",
            password=bcrypt.generate_password_hash("12345678").decode("utf-8"),
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

# Get all Movies
@app.route("/movies")
def all_movies():
    stmt = db.Select(Movie)
    movies = db.session.scalars(stmt).all()
    return movieSchema(many=True).dump(movies)



# delete Movie

#add the id to let the server know the Movie we want to delete
@app.route('/movies/<int:id>', methods=['DELETE'])
@jwt_required()
# includes the id parameter
def movie_delete(id):
    #get the user id invoking get_jwt_identity
    user_id = get_jwt_identity()
    # Find it in the db
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    # Make sure it is in the database
    if not user:
        return abort(401, description="Invalid user")
    # Stop the request if the user is not an admin
    if not user.admin:
        return abort(401, description="Unauthorised user")
    # find the Movie
    stmt = db.select(Movie).filter_by(id=id)
    movie = db.session.scalar(stmt)
    # return an error if the card doesn't exist
    if not movie:
        return abort(400, description="Movie doesn't exist")
    # Delete the movie from the database and commit
    db.session.delete(movie)
    db.session.commit()
    # return the card in the response
    return jsonify(movieSchema().dump(movie))



# Get all Actors
@app.route("/actors")
def all_actors():
    stmt = db.Select(Actor)
    actors = db.session.scalars(stmt).all()
    return actorSchema(many=True).dump(actors)


# DELETE ACTOR





















# User Signup
@app.route("/auth/signup", methods=["POST"])
def auth_register():
    # The request data will be loaded in a user_schema converted to JSON. request needs to be imported from
    user_fields = user_schema.load(request.json)
    # Find the email attribute
    stmt = db.select(User).filter_by(email=request.json['email'])
    user = db.session.scalar(stmt)
    
    if user:
        # return an abor message to inform the user. That will end the request
        return abort(400, description="Email already registered")
    # Create the user object
    user = User()
    #Add the email attribute
    user.email = user_fields["email"]
    # Add the password attribute hashed by bcrypt
    user.password = bcrypt.generate_password_hash(user_fields["password"]).decode("utf-8")
    # Set the admin attribute to false
    user.admin = False
    # Add it to the database and commit the changes
    db.session.add(user)
    db.session.commit()
    # Create a variable that sets an expiry date
    expiry = timedelta(days=1)
    # create the access token
    access_token = create_access_token(identity=str(user.id), expires_delta=expiry)
    # Return the user to check the request was successful
    return jsonify({"user": user.email, "token": access_token })

# User Login
@app.route('/auth/login', methods=['POST'])
def auth_login():
    # Get the user data from the request
    user_fields = user_schema.load(request.json)
    # find the user by email address
    stmt = db.select(User).filter_by(email=request.json['email'])
    user = db.session.scalar(stmt)
    # there is not a user with that email or if the password is no correct send an error
    if not user or not bcrypt.check_password_hash(user.password, user_fields['password']):
        return abort(401, description='Incorrect username and password') 
    
    # Create a variable that sets an expiry date
    expiry = timedelta(days=1)
    # Create the access token
    access_token = create_access_token(identity=str(user.id), expires_delta=expiry)
    # return the user email and the access token
    return jsonify({"user": user.email, "token": access_token})

# Get All users
@app.route("/users")
def all_users():
    stmt = db.Select(User)
    users = db.session.scalars(stmt).all()
    return users_schema.dump(users)

