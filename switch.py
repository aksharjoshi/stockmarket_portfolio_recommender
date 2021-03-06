import os
import sys
import logging
import psycopg2
import urlparse
from flask import Flask, jsonify
from flask import request
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
from flask.ext.heroku import Heroku
app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
cost = 0.16
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:////tmp/switch.db')
heroku = Heroku(app)
db = SQLAlchemy(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	control = db.Column(db.Integer)
	time = db.Column(db.DateTime)
	energy = db.Column(db.Float)
	def __init__(self, control, time, energy):
		self.control = control
		self.time = time
		self.energy = energy


@app.route('/switch_control/')
def switch_control():
	temp = User.query.get(1)
	if temp.control == 0:
		temp.control = 1
		temp.time = datetime.utcnow()
		db.session.commit()
	else:
		temp.control = 0
        end = datetime.utcnow()
        temp.energy = temp.energy + (end - temp.time).total_seconds() * cost
        temp.time = end
        db.session.commit()
	if temp.control == 0:
		list = [
        {'param': 'status', 'val': 0},
        {'param': 'energy', 'val': temp.energy}
    ]
		return jsonify(result = list)
	else:
		list = [
        {'param': 'status', 'val': 1}
    ]
    	return jsonify(result = list)

@app.route('/switch_reflect/')
def switch_reflect():
    var = request.args.get('status', '')
    temp = User.query.get(1)
    if  var == '0' and temp.control == 1:
        temp.control = 0
        end = datetime.utcnow()
        temp.energy = temp.energy + (end - temp.time).total_seconds() * cost
        temp.time = end
        db.session.commit()

    elif var == '1' and temp.control == 0:
	    temp.control = 1
	    temp.time = datetime.utcnow()
	    db.session.commit()

    return 'The switch status has been updated' 

@app.route('/')
def hello():
    temp = User.query.get(1)
    if temp == None:
        temp = User(0, datetime.utcnow(), 0)
        db.session.add(temp)
        db.session.commit()
    list = [
        {'param': 'message', 'val': 'connected', 'status': temp.control}
    ]
    return jsonify(result = list)

@app.route('/check_powercost')
def power_energy():
    temp = User.query.get(1)
    total = 0
    if temp.control == 0:
    	total = temp.energy
    elif temp.control == 1:
    	end = datetime.utcnow()
    	total = temp.energy + (end - temp.time).total_seconds() * cost
    db.session.commit()
    list = [
        {'param': 'energy', 'val': total}
    ]
    return jsonify(result = list)


@app.route('/reset')
def reset():
    temp = User.query.get(1)
    if temp == None:
        temp = User(0, datetime.utcnow(), 0)
        db.session.add(temp)
        db.session.commit()
    else:
       temp.energy = 0
       temp.time = datetime.utcnow()
       temp.control = 0
       db.session.commit()
    return 'The switch status has been reset' 

@app.route('/check_status')
def check_status():
    temp = User.query.get(1)
    status = temp.control
    list = [
        {'param': 'switch_status', 'val': status}
    ]
    db.session.commit()
    return jsonify(result = list)




if __name__ == '__main__':
    db.create_all()
    app.run(debug = True)