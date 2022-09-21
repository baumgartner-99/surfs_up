#import dependencies
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# access SQLite database
engine = create_engine("sqlite:///hawaii.sqlite")

#reflect the database into classes
Base = automap_base()
Base.prepare(engine, reflect=True)

#save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#create session link
session = Session(engine)

# set up flask
app = Flask(__name__)

#creating the welcome route
@app.route("/")
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')

# create precipitation route
    #calculate date from one year ago with most recent date
    # write query to get datae and precip from previous year
    # create dictionary with date as key and precip as value
@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
      filter(Measurement.date >= prev_year).all()
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

#create stations route
    # create query to get all stations
    # unravel results into one dimensional array and 
    # convert unraveled results to list
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

# create monthly temperature route
    # calculate date one year ago from last date
    # query primary station for all temp observations from previous year
    # unravel results into array and convert to list
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

# create summary statistics route
    # need to provide a start and end date - add an if-not statement
    # create query to select min, avg, and max temps
    # unravel results and convert to list
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)

#result from running above code is null because we have not specified start and end date
# can be fixed by entering any date in dataset as start and end in url address