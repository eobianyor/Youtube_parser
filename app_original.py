# import necessary libraries
import os
import pandas as pd
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)
# from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from datetime import datetime

from config import dbuser, dbpassword, dbhost, dbport, dbname

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Database Setup
#################################################

# try:
#     db_uri = os.environ['DATABASE_URL']
# except KeyError:
#     db_uri = "Insert Local Database"

# print(db_uri)
# app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

# db = SQLAlchemy(app)

# Connect session or connection to db
# session = Session(engine)
# connection = engine.connect()

# Connect to Database - Alternative
engine = create_engine(
    # f"postgres://{dbuser}:{dbpassword}@{dbhost}:{dbport}/{dbname}")
    f'postgresql://{dbuser}:{dbpassword}@database-1.cvmfiiilpm7y.us-east-1.rds.amazonaws.com:{dbport}/{dbname}')

session = Session(engine)
connection = engine.connect()

youtubeVids = pd.read_sql(f"SELECT * FROM youtube_table", connection)

connection.close()
session.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/data/<country>")
def data(country):
    ##### Open a session/connection #####

    singleCountry_youtubeVids = youtubeVids[youtubeVids["country"] == country]

    singleCountry_youtubeVids = singleCountry_youtubeVids.to_dict(
        orient='records')
    ##### Close the session/connection #####

    ##### Return a json which could be parsed further using js #####
    return jsonify(singleCountry_youtubeVids)


@app.route("/bar/<country>/<metric>")
def bar(country, metric):

    barData = youtubeVids[youtubeVids["country"] == country]

    barData = barData.groupby('categoryId').sum()
    barData = barData[metric]
    barData = barData.to_dict()

    return jsonify(barData)


@app.route("/line/<country>/<metric>")
def line(country, metric):
    lineData = youtubeVids[youtubeVids["country"] == country]
    # add a timestamp column to dataframe
    timestamps = []
    for index, row in lineData.iterrows():
        t = row["publishedAt"]
        td = datetime(t.year, t.month, t.day)
        datetime.timestamp(td)
        timestamps.append(datetime.timestamp(td))
    lineData["timestamp"] = timestamps
    # get top three categories
    topThree = list(lineData.groupby(["categoryId"]).sum()[
                    "likes"].sort_values(ascending=False).index[0:3])
    # Select one category and group by timeStamp
    first = lineData[lineData["categoryId"] == topThree[0]]
    first = first.groupby("timestamp").sum()
    first = first[metric].to_dict()
    return jsonify(first)


if __name__ == "__main__":
    app.run(debug=True)
