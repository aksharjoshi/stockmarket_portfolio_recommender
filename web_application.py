from flask import Flask, render_template, send_from_directory, session, request
import os
import sys
import logging
import psycopg2
import urlparse
import urllib2 
import json
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
from time import gmtime, strftime
from flask.ext.heroku import Heroku
from flask_bootstrap import Bootstrap
app = Flask(__name__)
Bootstrap(app)
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

class Stock:
    def __init__(self, name, current_condition, single_value):
        self.name = name
        self.current_condition = current_condition
        self.quantity = 0
        self.value = 0
        self.single_value = single_value
    def buy_stock(self, quantity, value):
        self.quantity = quantity
        self.value = value


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

@app.route("/finance_analysis", methods=['GET', 'POST'])
def finance_analysis():
    ethical_stock_name = ['AAPL', 'ADBE', 'NSRGY']
    growth_stock_name = ['IUSG', 'VONG', 'SCHG']
    index_stock_name = ['VTI', 'IXUS', 'ILTB']
    quality_stock_name = ['FB', 'MSFT', 'GOOG']
    value_stock_name = ['AMZN', 'ETN', 'CMI']
    if request.method == 'POST':
        ethical, growth, index, quality, value = False, False, False, False, False
        total_stock_list = []
        nameAndValue = []
        if request.form.get("ethical"):
            ethical = True
            if request.form.get("1"):
                total_stock_list.append('AAPL')
            if request.form.get("2"):
                total_stock_list.append('ADBE')
            if request.form.get("3"):
                total_stock_list.append('NSRGY')
        if request.form.get("growth"):
            growth = True
            if request.form.get("4"):
                total_stock_list.append('IUSG')
            if request.form.get("5"):
                total_stock_list.append('VONG')
            if request.form.get("6"):
                total_stock_list.append('SCHG')
        if request.form.get("index"):
            index = True
            if request.form.get("7"):
                total_stock_list.append('VTI')
            if request.form.get("8"):
                total_stock_list.append('IXUS')
            if request.form.get("9"):
                total_stock_list.append('ILTB')
        if request.form.get("quality"):
            quality = True
            if request.form.get("10"):
                total_stock_list.append('FB')
            if request.form.get("11"):
                total_stock_list.append('MSFT')
            if request.form.get("12"):
                total_stock_list.append('GOOG')
        if request.form.get("value"):
            value = True
            if request.form.get("13"):
                total_stock_list.append('AMZN')
            if request.form.get("14"):
                total_stock_list.append('ETN')
            if request.form.get("15"):
                total_stock_list.append('CMI')
        for val in total_stock_list:
            price, change, perchange = fetchPreMarket(val)
            if change == "error":
                continue
            url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(val)
            result = requests.get(url).json()
            real_name = 'unknown'
            for x in result['ResultSet']['Result']:
                if x['symbol'] == val:
                    real_name=x['name']
                    break
            #condition = change + ' ' + '(' + str(perchange) + ')'
            temp = Stock(real_name, 'hello', price)
            nameAndValue.append(temp)
        stockname = request.form['stockname']
        total_money = request.form['amount']
        price, change, perchange = fetchPreMarket(stockname)
        if change == "error":
            return render_template('invalid.html')
        url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(stockname)
        result = requests.get(url).json()
        check_time = strftime("%a %d %b %Y %H:%M:%S %Z", gmtime())
        real_name = 'unknown'
        for x in result['ResultSet']['Result']:
            if x['symbol'] == stockname:
                real_name=x['name']
                break
        s = str(price) + ' ' + change + ' ' + '(' + str(perchange) + ')'
        return render_template('engine_recommend_result.html', checktime=check_time, result=s, stock_name=real_name, nameAndValue=nameAndValue)
    return render_template('finance_analysis.html')

def fetchPreMarket(symbol):
    link = "http://finance.google.com/finance/info?client=ig&q="
    url = link+"%s:%s" % ("NASDAQ", symbol)
    try:
        u = urllib2.urlopen(url)
        content = u.read()
        data = json.loads(content[3:])
        info = data[0]
        price = float(info["l_fix"])
        base = float(info["pcls_fix"])
        if base == 0:
            return ("", "error", "")
        change = info["c"]
        perchange = '{:+.2%}'.format((price - base)/base)
        return (price, change, perchange)
    except (urllib2.HTTPError, urllib2.URLError), err:
        return (err, "error", "")


# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
if __name__ == '__main__':
    app.run(debug = True)