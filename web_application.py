from flask import Flask, render_template, send_from_directory, session, request
import os
import sys
import logging
#import psycopg2
import urlparse
#from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
#from flask.ext.heroku import Heroku
app = Flask(__name__)
#app.logger.addHandler(logging.StreamHandler(sys.stdout))
#app.logger.setLevel(logging.ERROR)
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:////tmp/web_application.db')
#heroku = Heroku(app)
#db = SQLAlchemy(app)

#class WebUser(db.Model):
#	id = db.Column(db.Integer, primary_key=True)
#	name = db.Column(db.String(80))
#	time = db.Column(db.DateTime)
#	password = db.Column(db.String(80))
#	email = db.Column(db.String(80))
#	def __init__(self, name, time, password, email):
#		self.name = name
#		self.time = time
#		self.password = password
#		self.email = email


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
        allotment = request.form['allotment']
        finalSharePrice = request.form['finalSharePrice']
        sellCommision = request.form['sellCommision']
        initialSharePrice = request.form['initialSharePrice']
        buyCommision = request.form['buyCommision']
        taxRate = request.form['taxRate']
        symbol_name = ""
        url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol)
        result = request.get(url).json()
        for x in result['ResultSet']['Result']:
            if x['symbol'] == argv:
                symbol_name =  x['name']
                break
        totalSell = allotment * finalSharePrice
        initialPaid = allotment * initialSharePrice
        pureProfit = totalSell - initialPaid
        taxPaid = 0
        if pureProfit > 0:
            taxPaid = pureProfit * taxRate / 100
        totalCost = sellCommision + buyCommision + initialPaid + taxPaid
        returnRate = (totalSell - totalCost) / totalCost / 100
        breakEven = (sellCommision + buyCommision) / allotment + initialSharePrice
        totalSell = '{:.2%}'.format(totalSell)
        totalCost = '{:.2%}'.format(totalCost)
        initialPaid = '{:.2%}'.format(initialPaid)
        buyCommision = '{:.2%}'.format(buyCommision)
        sellCommision = '{:.2%}'.format(sellCommision)
        taxPaid = '{:.2%}'.format(taxPaid)
        pureProfit = '{:.2%}'.format(pureProfit)
        netProfit = '{:.2%}'.format(totalSell - totalCost)
        returnRate = '{:.2%}'.format(returnRate)
        breakEven = '{:.2%}'.format(breakEven)
        return render_template('calculator.html', totalSell=totalSell)
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

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
if __name__ == '__main__':
    app.run()
    app.run(debug = True)