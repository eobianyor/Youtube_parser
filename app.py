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
# youtubeVids = pd.read_sql(f"SELECT * FROM youtube_table2", connection)
# Fix the 29 vs Non profits issue
youtubeVids['categoryId'] = youtubeVids['categoryId'].replace(
    ["29"], "Nonprofits & Activism")

# Rename Columns
youtubeVids = youtubeVids.rename(columns={'country': 'country', 'video_id': 'video_id', 'title': 'title', 'publishedAt': 'publishedAt', 'channelTitle': 'channelTitle', 'categoryId': 'categoryId',
                                          'trending_date': 'trending_date', 'view_count': 'views', 'likes': 'likes', 'dislikes': 'dislikes', 'comment_count': 'comments', 'thumbnail_link': 'thumbnail_link'})
connection.close()
session.close()

#################################################
# HOME ROUTE
#################################################
@app.route("/")
def home():
    return render_template("index.html")

#################################################
# ROUTES FOR DROP DOWN MENU
#################################################
@app.route("/dropdown1")
def dropdown1():
    country_df = youtubeVids['country'].value_counts()
    countryList = country_df.index.tolist()
    return jsonify(countryList)


@app.route("/dropdown2")
def dropdown2():
    youtubeVids['categoryId'] = youtubeVids['categoryId'].replace(
        ["29"], "Nonprofits & Activism")
    category_df = youtubeVids['categoryId'].value_counts()
    categoryList = category_df.index.tolist()
    return jsonify(categoryList)


@app.route("/dropdown3")
def dropdown3():
    metricList = ['views', 'likes', 'dislikes', 'comments']
    return jsonify(metricList)

#################################################
# ROUTES FOR DATA
#################################################

####################### ROUTE FOR BAR GRAPH 1 ##########################
@app.route("/dataset1/<country>/<metric>")
def dataset1(country, metric):
    # Fix the 29 vs Non profits issue
    youtubeVids['categoryId'] = youtubeVids['categoryId'].replace(
        ["29"], "Nonprofits & Activism")

    # Sort dataframe by country & category & metric
    barGraph1Data = youtubeVids[youtubeVids["country"] == country]
    barGraph1Data = barGraph1Data.groupby('categoryId').mean()
    barGraph1Data = barGraph1Data[metric]

    ##### Convert data to a dictionary #####
    barGraph1Data = barGraph1Data.to_dict()
    ##### Jsonify the data #####
    return jsonify(barGraph1Data)

####################### ROUTE FOR BAR GRAPH 2 ##########################
@app.route("/dataset2/<country>/<category>/<metric>")
def dataset2(country=None, category=None, metric=None):
    # Fix the 29 vs Non profits issue
    youtubeVids['categoryId'] = youtubeVids['categoryId'].replace(
        ["29"], "Nonprofits & Activism")

    # Sort dataframe by country & category & select columns to keep
    barGraph2Data = youtubeVids[youtubeVids["country"] == country]
    barGraph2Data = barGraph2Data[barGraph2Data["categoryId"] == category]
    barGraph2Data = barGraph2Data.loc[:, [
        "views", "comments", "likes", "dislikes", "country", "categoryId"]]

    # Create a table (df) of metric values vs the count of each valus for bargraph
    metric_values = ["views", "comments", "likes", "dislikes"]
    metricMaxValues = []
    n = 0
    for metric in metric_values:
        step1_df = barGraph2Data.sort_values(by=metric, ascending=False)
        step2_df = step1_df[metric]
        step3 = step2_df.values.tolist()
        metricMaxValues.append(step3[0])

    # Create the actual table (df)
    barGraph2_df = pd.DataFrame(
        {'Metric_Values': metric_values,
         'Max_Value': metricMaxValues
         })
    ##### Convert data to a dictionary #####
    barGraph2_df = barGraph2_df.to_dict()
    ##### Jsonify the data #####
    return jsonify(barGraph2_df)

####################### ROUTE FOR LINE GRAPH ##########################
@app.route("/dataset3/<country>/<metric>")
def dataset3(country, metric):
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

    ##### Convert data to a dictionary #####
    first = first[metric].to_dict()
    ##### Jsonify the data #####
    return jsonify(first)

####################### ROUTE FOR TOP 10 TABLE ##########################
@app.route("/dataset4/<country>/<category>/<metric>")
def dataset4(country=None, category=None, metric=None):
    # Fix the 29 vs Non profits issue
    youtubeVids['categoryId'] = youtubeVids['categoryId'].replace(
        ["29"], "Nonprofits & Activism")

    # Sort dataframe by country & category
    table_df = youtubeVids[youtubeVids["country"] == country]
    table_df = table_df[table_df["categoryId"] == category]

    # print('metric=', metric)
    # Sort dataframe (largest to smallest) by metric selected
    sorted_table_df = table_df.sort_values(by=metric, ascending=False)

    # Remove duplicate videos from dataframe
    sorted_table_df = sorted_table_df.drop_duplicates(
        subset='title', keep="first")

    # print('metric=', metric)
    # Select top 10 (based on metric selected) from dataframe
    top10TableData_df = sorted_table_df.nlargest(10, metric)

    # Select columns to keep for table
    top10TableData_df = top10TableData_df[['categoryId', 'country', 'title', 'channelTitle',
                                           'views', 'comments', 'trending_date', 'likes', 'dislikes', 'video_id', 'thumbnail_link']]

    ##### Convert data to a dictionary #####
    top10TableData = top10TableData_df.to_dict(orient="records")
    ##### Jsonify the data #####
    # print(jsonify(top10TableData))
    return jsonify(top10TableData)
# return render_template('test_out.html', data=top10TableData)

#################################################
# # @app.route("/data/<country>")
# # def data(country):
# #     ##### Open a session/connection #####

# #     singleCountry_youtubeVids = youtubeVids[youtubeVids["country"] == country]

# #     singleCountry_youtubeVids = singleCountry_youtubeVids.to_dict(
# #         orient='records')
# #     ##### Close the session/connection #####

# #     ##### Return a json which could be parsed further using js #####
# #     return jsonify(singleCountry_youtubeVids)


# @app.route("/bar/<country>/<metric>")
# def bar(country, metric):

#     barData = youtubeVids[youtubeVids["country"] == country]

#     barData = barData.groupby('categoryId').sum()
#     barData = barData[metric]
#     barData = barData.to_dict()

#     return jsonify(barData)


# @app.route("/line/<country>/<metric>")
# def line(country, metric):
#     lineData = youtubeVids[youtubeVids["country"] == country]
#     # add a timestamp column to dataframe
#     timestamps = []
#     for index, row in lineData.iterrows():
#         t = row["publishedAt"]
#         td = datetime(t.year, t.month, t.day)
#         datetime.timestamp(td)
#         timestamps.append(datetime.timestamp(td))
#     lineData["timestamp"] = timestamps
#     # get top three categories
#     topThree = list(lineData.groupby(["categoryId"]).sum()[
#                     "likes"].sort_values(ascending=False).index[0:3])
#     # Select one category and group by timeStamp
#     first = lineData[lineData["categoryId"] == topThree[0]]
#     first = first.groupby("timestamp").sum()
#     first = first[metric].to_dict()
#     return jsonify(first)


# # @app.route("/dataCat/<country>")
# @app.route("/dataCat/<country>/<category>/<metric>")
# def dataCat(country=None, category=None, metric=None):
#     countryData = youtubeVids[youtubeVids["country"] == country]
#     country_Cat_Data = countryData[countryData["categoryId"] == category]
#     finalFilteredData = country_Cat_Data[country_Cat_Data["categoryId"] == category]

#     finalFilteredData = finalFilteredData.to_dict()

#     return jsonify(finalFilteredData)
#################################################

@app.route("/allData")
def allData():
    allData = youtubeVids

    allData = allData.to_dict()

    return jsonify(allData)


if __name__ == "__main__":
    app.run(debug=True)
