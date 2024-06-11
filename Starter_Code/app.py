# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import pandas as pd


from flask import Flask, jsonify


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


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route('/')
def welcome():
    """List All Available API routes."""
    return(f'available routes<br/>'
           f'/api/v1.0/precipitation<br/>'
           f'/api/v1.0/stations<br/>'
           f'/api/v1.0/tobs<br/>'
           f'/api/v1.0/<start><br/>'
           f'/api/v1.0/<start>/<end>')


@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)

    last_year_start = dt.datetime.strptime('2017-08-23', '%Y-%m-%d') - dt.timedelta(days=365)

    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= last_year_start).all()

    session.close()

    past_year_results = []
    for date, prcp in results:
        last_year_results = {}
        last_year_results[date] = prcp
        past_year_results.append(last_year_results)

    return jsonify(past_year_results)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)

    results = session.query(station.id, station.station, station.name, station.latitude, station.longitude, station.elevation).all()

    stations_result = []
    for id, stations, name, latitude, longitude, elevation in results:
        station_dict = {}
        station_dict['id'] = id
        station_dict['stations'] = stations
        station_dict['name'] = name
        station_dict['latitude'] = latitude
        station_dict['longitude'] = longitude
        station_dict['elevation'] = elevation
        stations_result.append(station_dict)

    return jsonify(stations_result)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    most_active_stations = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    most_active = most_active_stations[0][0]
    last_year_start = dt.datetime.strptime('2017-08-23', '%Y-%m-%d') - dt.timedelta(days=365)
    results = session.query(measurement.date, measurement.tobs).filter(measurement.date >= last_year_start).filter(measurement.station == most_active).all()
    session.close

    temp = []
    for date, tobs in results:
        date_dict = {}
        date_dict[date] = tobs
        temp.append(date_dict)

    return jsonify(temp)

@app.route('/api/v1.0/<start>')
def start(start):
    session = Session(engine)
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    results = session.query(func.min(measurement.tobs),func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start_date).all()

    session.close()
    start_tobs = []
    for min, max, avg in results:
        start_dict = {}
        start_dict['TMIN'] = min
        start_dict['TMAX'] = max
        start_dict['TAVG'] = avg
        start_tobs.append(start_dict)

    return jsonify(start_tobs)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start,end):
    session = Session(engine)
    start_date = dt.datetime.strptime(start,'%Y-%m-%d')
    end_date = dt.datetime.strptime(end,'%Y-%m-%d')

    results = session.query(func.min(measurement.tobs),func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start_date).filter(measurement.date <end_date).all()
    start_end_list = []
    for min, max, avg in results:
        start_end_dict = {}
        start_end_dict['TMIN'] = min
        start_end_dict['TMAX'] = max
        start_end_dict['TAVG'] = avg
        start_end_list.append(start_end_dict)

    return jsonify(start_end_list)

if __name__ == '__main__':
    app.run(debug=True)


