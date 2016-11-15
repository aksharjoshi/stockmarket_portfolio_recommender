from flask import Flask, render_template, send_from_directory, session, request
import os
import sys
import logging
import psycopg2
import urlparse
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
from time import gmtime, strftime
from flask.ext.heroku import Heroku
app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:////tmp/web_application.db')
heroku = Heroku(app)
db = SQLAlchemy(app)

class WebUser(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80))
	time = db.Column(db.DateTime)
	password = db.Column(db.String(80))
	email = db.Column(db.String(80))
	def __init__(self, name, time, password, email):
		self.name = name
		self.time = time
		self.password = password
		self.email = email


# controllers
#@app.route('/favicon.ico')
#def favicon():
#    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        symbol = request.form['symbol']
        allotment = float(request.form['allotment'])
        finalSharePrice = float(request.form['finalSharePrice'])
        sellCommision = float(request.form['sellCommission'])
        initialSharePrice = float(request.form['initialSharePrice'])
        buyCommision = float(request.form['buyCommission'])
        taxRate = float(request.form['taxRate']) / 100
        totalSell = allotment * finalSharePrice
        initialPaid = allotment * initialSharePrice
        pureProfit = totalSell - initialPaid - sellCommision - buyCommision
        taxPaid = 0
        session['flag'] = False;
        if pureProfit > 0:
            taxPaid = pureProfit * taxRate
            session['flag'] = True;
        totalCost = sellCommision + buyCommision + initialPaid + taxPaid
        returnRate = (totalSell - totalCost) / totalCost
        breakEven = (sellCommision + buyCommision) / allotment + initialSharePrice
        netProfit = '{:.2f}'.format(totalSell - totalCost)
        totalSell = '{:.2f}'.format(totalSell)
        totalCost = '{:.2f}'.format(totalCost)
        initialPaid = '{:.2f}'.format(initialPaid)
        buyCommision = '{:.2f}'.format(buyCommision)
        sellCommision = '{:.2f}'.format(sellCommision)
        taxPaid = '{:.2f}'.format(taxPaid)
        taxRate = '{:.2%}'.format(taxRate)
        pureProfit = '{:.2f}'.format(pureProfit)
        returnRate = '{:.2%}'.format(returnRate)
        breakEven = '{:.2f}'.format(breakEven)
        return render_template('calculator.html', totalSell=totalSell, totalCost=totalCost, netProfit=netProfit, initialPaid=initialPaid, buyCommision=buyCommision, sellCommision=sellCommision, taxPaid=taxPaid, pureProfit=pureProfit, returnRate=returnRate, breakEven=breakEven, allotment=allotment, initialSharePrice=initialSharePrice, taxRate=taxRate)
    return render_template('index.html')

@app.route("/logout")
def logout():
    session['logged_in'] = False;
    return render_template('index.html')

@app.route("/sign_up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['uname']
        pwd = request.form['psw']
        email = request.form['email']
        test = WebUser.query.filter_by(name=username).first()
        if test is not None:
    	    return render_template('userExisted.html', username=username)
        me = WebUser(name=username, time=datetime.utcnow(), password=pwd, email=email)
        app.logger.info(me.id)
        db.session.add(me)
        db.session.commit()
        session['username'] = username;
        session['logged_in'] = True;
        return render_template('index.html')
    return render_template('sign_up.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['uname']
        pwd = request.form['psw']
        test = WebUser.query.filter_by(name=username).filter_by(password=pwd).first()
        if test is None:
    		return render_template('noMatch.html')
        session['logged_in'] = True;
        session['username'] = username;
        return render_template('index.html')
    return render_template('login.html')

@app.route("/finance_analysis")
def finance_analysis():
    return render_template('finance_analysis.html')


# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
if __name__ == '__main__':
    app.run(debug = True)