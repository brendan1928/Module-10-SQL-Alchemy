# Import the dependencies.
import numpy as np
import matplotlib.pyplot as plt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime as dt
from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# Define date horizon
recent_date = dt.date(2017, 8, 23)
query_end_date = recent_date - dt.timedelta(days=365)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/temperature<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/precipitation"
    )

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all passenger names"""
    # Query all stations
    names = session.query(station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(names))

    return jsonify(all_names)

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Perform a query to retrieve the data and precipitation scores
    historical_prcp = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date <= recent_date).\
    filter(measurement.date >= query_end_date).all()
    session.close()
    # Convert list of tuples into normal list
    prcp_list = []
    for prcp, date in historical_prcp:
        prcp_dict = {}
        prcp_dict["Percipitation"] = prcp
        prcp_dict["Date"] = date
        prcp_list.append(prcp_dict)
    return jsonify(historical_prcp)

@app.route("/api/v1.0/tobs")
def tobs():
    # Perform a query to retrieve the data and precipitation scores
    tobs_data = session.query(measurement.tobs,func.count(measurement.tobs)).\
    filter(measurement.date <= recent_date).\
    filter(measurement.date >= query_end_date).\
    filter(measurement.station == 'USC00519281').group_by(measurement.tobs).all()
    session.close()
    # Convert list of tuples into normal list
    historical_tobs = []
    for temp, count in tobs_data:
        tobs_dict = {}
        tobs_dict["Temperature"] = temp
        tobs_dict["Frequency"] = count
        historical_tobs.append(tobs_dict)
    return jsonify(historical_tobs)

@app.route("/api/v1.0/start")
def start():
# Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
    summary = session.query(func.max(measurement.tobs),\
    func.min(measurement.tobs),func.avg(measurement.tobs)).\
    where(measurement.station == 'USC00519281').all()
    return jsonify(summary)