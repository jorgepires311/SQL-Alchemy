from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,inspect, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)
inspector = inspect(engine)
inspector.get_table_names()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurement.date, Measurement.prcp).all()
    precip = []
    for date, prcp in results:
        dictPrecip = {}
        dictPrecip[date]=prcp
        precip.append(dictPrecip)
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station,Station.name).all()
    stations = []
    for station,name in results:
        dictStation = {}
        dictStation[station] = name
        stations.append(dictStation)
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    lastDateQuery = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    for date in lastDateQuery:
        latestDate = date
    query_date = latestDate.split('-')
    yrAgo = dt.date(int(query_date[0]),int(query_date[1]),int(query_date[2])) - dt.timedelta(days=365)
    results = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= yrAgo).filter(Measurement.date <= latestDate).order_by(Measurement.date).all()
    lastYear = []
    for date,prcp in results:
        dictLastYear = {}
        dictLastYear[date] = prcp
        lastYear.append(dictLastYear)
    return jsonify(lastYear)

@app.route("/api/v1.0/<start>")
def datePRCP(start):
    lastDateQuery = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    for date in lastDateQuery:
        latestDate = date
    sel = [func.min(Measurement.prcp).label('min'),func.max(Measurement.prcp).label('max'),func.avg(Measurement.prcp).label('avg')]
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= latestDate).order_by(Measurement.date).all()
    prcpDate = []
    for min,max,avg in results:
        dictPrcpDate = {}
        dictPrcpDate['start'] = start
        dictPrcpDate['end'] = latestDate
        dictPrcpDate['min'] = min
        dictPrcpDate['max'] = max
        dictPrcpDate['avg'] = avg
        prcpDate.append(dictPrcpDate)
    return jsonify(prcpDate)

@app.route("/api/v1.0/<start>/<end>")
def dateRange(start,end):
    sel = [func.min(Measurement.prcp).label('min'),func.max(Measurement.prcp).label('max'),func.avg(Measurement.prcp).label('avg')]
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).order_by(Measurement.date).all()
    prcpRange = []
    for min,max,avg in results:
        dictPrcpRange = {}
        dictPrcpRange['start'] = start
        dictPrcpRange['end'] = end
        dictPrcpRange['min'] = min
        dictPrcpRange['max'] = max
        dictPrcpRange['avg'] = avg
        prcpRange.append(dictPrcpRange)
    return jsonify(prcpRange)

if __name__ == '__main__':
    app.run(debug=True)