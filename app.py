# Import dependencies
from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

import numpy as np
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

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



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
            f"Welcome to the Honolulu Climate Analysis API!<br/>"
            f"Avalable Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/start<br/>"
            f"/api/v1.0/start/end<br/>" 
            f"<p>'start' and 'end' date should be in the format MMDDYYYY<p>"   
            )

@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= prev_year)
    session.close()
    precip = { date: prcp for date, prcp in precipitation}
    return jsonify(precip)  

@app.route("/api/v1.0/stations") 
def stations():
    stations_query = session.query(station.station).all()
    session.close()
    station_list = list(np.ravel(stations_query))
    return jsonify(stations = station_list)

@app.route("/api/v1.0/tobs")
def temperature():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temperature = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= prev_year).\
        filter(measurement.station == "USC00519281")
    session.close()
    temp_dict = { date:tobs for date, tobs in temperature}
    return jsonify(temperature_observations = temp_dict)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_date_range(start=None, end=None):
    
    sel = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]

    if end == None:
        start = dt.datetime.strptime(start, "%m%d%Y")    
        results = session.query(*sel).\
            filter(measurement.date >= start).all()

        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps=temps)

    start = dt.datetime.strptime(start, "%m%d%Y") 
    end = dt.datetime.strptime(end, "%m%d%Y")

    results = session.query(*sel).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()

    session.close()

    temps = list(np.ravel(results))

    return jsonify(temps=temps)


if __name__ == '__main__':
    app.run(debug=True)