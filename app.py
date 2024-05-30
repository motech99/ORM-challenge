from flask import Flask, jsonify
app = Flask(__name__)

## DB CONNECTION AREA

# CLI COMMANDS AREA

# MODELS AREA

# SCHEMAS AREA

# ROUTING AREA

@app.route("/")
def hello():
  return "Welcome to Ripe Tomatoes API"
