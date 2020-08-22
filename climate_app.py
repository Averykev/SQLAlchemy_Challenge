###Import the dependencies I will need

from flask import Flask, jsonify

import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt 

###Database Setup

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect = True)

Measurement = Base.classes.measurement

Station = Base.classes.station

session = Session(engine)

###Flask Setup

app = Flask(__name__)

###Flask Routes

@app.route("/")
def welcome():
    return(f"Welcome to the Surf's Up Climate API!<hr/>"

     f"Available Routes:<br/>"
     f"/api/v1.0/precipitation  ----->  Precipitation totals for the latest year of data<br/>"
     f"/api/v1.0/stations  ----->  This is a list of the observation stations<br/>"
     f"/api/v1.0/tobs  ----->  The last year of termperature data for the most active observation station<br/>"
     f"/api/v1.0/datesearch/start_date  ----->  Low, high, and average temperature for every day after the start date.  Enter start date in 'YYYY-MM-DD' format<br/>"
     f"/api/v1.0/datesearch/start_date/end_date  ----->  Low, high, and average temperature for every day between the date range given.  Enter start and end date in 'YYYY-MM-DD' format<hr/>"

     f"Data is available from January 1st, 2010 up to August 23rd, 2017<hr/>")


@app.route("/api/v1.0/precipitation")
def precipitation():

    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    latest_date = latest_date[0]

    one_year_ago = dt.datetime.strptime(latest_date, "%Y-%m-%d") - dt.timedelta(days=365)

    results_prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).order_by((Measurement.date).desc()).all()

    results_prcp = list(results_prcp)

    return jsonify(results_prcp)



@app.route("/api/v1.0/stations")
def stations():

    station_list = session.query(Station.station, Station.name).all()

    results_stations = list(np.ravel(station_list))

    return jsonify(results_stations)



@app.route("/api/v1.0/tobs")
def tobs():

    latest_date_tobs = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    latest_date_tobs = latest_date_tobs[0]

    one_year_ago_tobs = dt.datetime.strptime(latest_date_tobs, "%Y-%m-%d") - dt.timedelta(days=365)

    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()

    most_active_station = most_active_station[0]

    temp_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago_tobs).filter(Measurement.station == most_active_station).order_by(Measurement.date).all()

    temp_results = list(np.ravel(temp_results))

    return jsonify(temp_results)



@app.route("/api/v1.0/datesearch/<start>")
def start(start=None):

    start_date = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()

    start_date_list = list(start_date)

    return jsonify(start_date_list)



@app.route("/api/v1.0/datesearch/<start>/<end>")
def start_end(start=None, end=None):

    date_range = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date>=start).filter(Measurement.date<=end).group_by(Measurement.date).all()

    date_range_list = list(date_range)

    return jsonify(date_range_list)


if __name__ == "__main__":
    app.run(debug=True)