# import necessary libraries
import os
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)

from flask_sqlalchemy import SQLAlchemy

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Database Setup
#################################################

try:
    db_uri = os.environ['DATABASE_URL']
except KeyError:
    db_uri = "Insert Local Database"

print(db_uri)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

db = SQLAlchemy(app)

@app.route("/")
def home():
    return render_template("index.html", data=db)



if __name__ == "__main__":
    app.run()