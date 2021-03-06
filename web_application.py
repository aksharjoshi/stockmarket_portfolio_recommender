from flask import Flask, render_template, send_from_directory, session, request
import os
import sys
import logging
import MySQLdb
#mysql.connector
#import psycopg2
import urlparse
import urllib2 
import json
#from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from yahoo_finance import Share
import requests
from time import gmtime, strftime
#from flask.ext.heroku import Heroku
from flask_bootstrap import Bootstrap
app = Flask(__name__)
Bootstrap(app)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:////tmp/web_application.db')
#heroku = Heroku(app)
#db = SQLAlchemy(app)

#class WebUser(db.Model):
#   id = db.Column(db.Integer, primary_key=True)
#   name = db.Column(db.String(80))
#   time = db.Column(db.DateTime)
#   password = db.Column(db.String(80))
#   email = db.Column(db.String(80))
#   def __init__(self, name, time, password, email):
#       self.name = name
#       self.time = time
#       self.password = password
#       self.email = email


# controllers
#@app.route('/favicon.ico')
#def favicon():
#    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')

#Global variables
cnx=""
cursor=""
query=""

class Stock:
    def __init__(self, name, condition, single_value, symbol):
        self.name = name
        self.condition = condition
        self.quantity = 0
        self.value = 0
        self.single_value = single_value
        self.symbol = symbol
    def buy_stock(self, quantity):
        self.quantity = quantity

    def set_value(self, value):
        self.value = value

    def printVal(self):
        print self.name
        print self.condition
        print self.quantity
        print self.value
        print self.single_value
        print self.symbol

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return 'Hello'
    nameAndValue = []
    cnx = MySQLdb.connect("portfolio-db.cxbh37qczpuy.us-west-1.rds.amazonaws.com","root", "stock_portfolio" , "stock_portfolio")
    cursor = cnx.cursor()
    query = "SELECT company_name, quantity FROM USER_PORTFOLIO WHERE username='"+session['username']+"';"
    print session['username']
    cursor.execute(query)
    if cursor.rowcount is not 0:
        for company,quantity in cursor:
            stock = fetchTotalInfo(company)
            stock.buy_stock(quantity)
            stock.set_value(float(stock.quantity) * float(stock.single_value))
            nameAndValue.append(stock)
    fiveDaysData = []
    start = datetime.today() - timedelta(days=7)
    end = datetime.today() - timedelta(days=1)
    start = start.strftime('%Y-%m-%d')
    end = end.strftime('%Y-%m-%d')
    for i in range(5):
        fiveDaysData.append(0)
    for val in nameAndValue:
        stock = Share(val.symbol)
        data = stock.get_historical(str(start),str(end))
        count = 0
        for detail in data:
            value = float(detail['Close'])
            #if value == 0:
             #   continue
            fiveDaysData[count] = fiveDaysData[count] + value * float(val.quantity)
            count = count + 1
    fiveDaysData.reverse()
    maxValue = max(fiveDaysData) + 100
    minValue = min(fiveDaysData) - 100
    return render_template('index.html',fiveDaysData=fiveDaysData, maxValue=maxValue, minValue=minValue, nameAndValue=nameAndValue)

@app.route("/logout")
def logout():
    session['logged_in'] = False;
    session['username'] = '';
    fiveDaysData = []
    for i in range(5):
        fiveDaysData.append(0)
    maxValue = 0
    minValue = 0
    nameAndValue=[]
    return render_template('index.html',fiveDaysData=fiveDaysData, maxValue=maxValue, minValue=minValue, nameAndValue=nameAndValue)


@app.route("/sign_up", methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['uname']
        pwd = request.form['psw']
        email = request.form['email']

        query="Select * from USER where username='"+username+"';"
        print username

        cursor.execute(query)
        for databases in cursor:
            print databases
            print "\n"

        if cursor.fetchone() is not None:
            print "inside if"
            return render_template('userExisted.html', username=username)
        else:
            query = "INSERT INTO USER (username, password, email) VALUES ('"+username+"', '"+pwd+"', '"+email+"');"
            print "query in insert: " + query
            try:
                cursor.execute(query)

                for o in cursor:
                    print o

                if cursor.lastrowid:
                    print('last insert id', cursor.lastrowid)
                else:
                    print('last insert id not found')
 
                cnx.commit()
                session['username'] = username;
                session['logged_in'] = True;
            except Exception as e:
                raise e
            
            return render_template('index.html',fiveDaysData=[], maxValue=0, minValue=0,nameAndValue=[])
    return render_template('sign_up.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['uname']
        pwd = request.form['psw']
      #   test = WebUser.query.filter_by(name=username).filter_by(password=pwd).first()
      #   if test is None:
            # return render_template('noMatch.html')
        query = "SELECT * FROM USER WHERE username='"+username+"' AND password='"+pwd+"';"
        cursor.execute(query)

        if cursor.fetchone() is None:
            print "inside if"
            return render_template('wrongCred.html', username=username)
        else:
            session['logged_in'] = True;
            session['username'] = username;
            nameAndValue = []
            cnx = MySQLdb.connect("portfolio-db.cxbh37qczpuy.us-west-1.rds.amazonaws.com","root", "stock_portfolio" , "stock_portfolio")
            cursorone = cnx.cursor()
            query = "SELECT username,password,company_name,quantity FROM USER_PORTFOLIO WHERE username='"+session['username']+"';"
            cursorone.execute(query)
            if cursorone.rowcount is not 0:
                for username,password,company,quantity in cursorone:
                    stock = fetchTotalInfo(company)
                    stock.buy_stock(quantity)
                    stock.set_value(float(stock.quantity) * float(stock.single_value))
                    nameAndValue.append(stock)
            fiveDaysData = []
            start = datetime.today() - timedelta(days=7)
            end = datetime.today() - timedelta(days=1)
            start = start.strftime('%Y-%m-%d')
            end = end.strftime('%Y-%m-%d')
            for i in range(5):
                fiveDaysData.append(0)
            for val in nameAndValue:
                stock = Share(val.symbol)
                data = stock.get_historical(str(start),str(end))
                count = 0
                for detail in data:
                    value = float(detail['Close'])
                    if value == 0:
                        continue
                    fiveDaysData[count] = fiveDaysData[count] + value * float(val.quantity)
                    count = count + 1
            fiveDaysData.reverse()
            maxValue = max(fiveDaysData) + 100
            minValue = min(fiveDaysData) - 100
            return render_template('index.html',fiveDaysData=fiveDaysData, maxValue=maxValue, minValue=minValue,nameAndValue=nameAndValue)
    return render_template('login.html')

@app.route("/firstPage")
def firstPage():
    query = "SELECT company_name, share_quantity from USER_HISTORY WHERE userid='"+session['username']+"';"
    cursor.execute(query)
    cnx.commit()
    for name, quantity in cursor:
        print name
        print quantity
    return "Hello"

@app.route("/finance_analysis", methods=['GET', 'POST'])
def finance_analysis():
    if session['logged_in'] == True:
        #print "Request headers are: " + request.headers
        ethical_stock_name = ['AAPL', 'ADBE', 'NSRGY']
        growth_stock_name = ['IUSG', 'VONG', 'SCHG']
        index_stock_name = ['VTI', 'IXUS', 'ILTB']
        quality_stock_name = ['FB', 'MSFT', 'GOOG']
        value_stock_name = ['AMZN', 'ETN', 'CMI']
        # if request.method == 'GET':
        #     query = "SELECT company_name, share_quantity from USER_HISTORY WHERE userid='"+[session'username']+"';"
        #     cursor.execute(query)
        #     cnx.commit()
        #     for name, quantity in cursor:
        #         print name
        #         print quantity



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
            print "Total stock list: "
            print total_stock_list
            print "money is: " + request.form['amount']
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
                condition = change + ' ' + '(' + str(perchange) + ')'
                temp = Stock(real_name, condition, float(price), val)
                nameAndValue.append(temp)
            total_money = request.form['amount']

            print "name value is : "
            for name in nameAndValue:
                print name.printVal()
            cnx = MySQLdb.connect("portfolio-db.cxbh37qczpuy.us-west-1.rds.amazonaws.com","root", "stock_portfolio" , "stock_portfolio")
            cursor = cnx.cursor()
            nameValue, leftAmount = RRgetQuantity(nameAndValue, total_money)
            for x in nameValue:
                check_quantity = str(x.quantity)
                check_symbol = str(x.symbol)
                query = "SELECT quantity FROM USER_PORTFOLIO WHERE username='"+session['username']+"' AND company_name='"+check_symbol+"';"
                cursor.execute(query)
                if cursor.rowcount == 0:
                    print 'hello'
                    query = "INSERT INTO USER_PORTFOLIO(username,company_name,quantity,last_modified) VALUES('"+session['username']+"', '"+check_symbol+"', '"+check_quantity+"','');"
                    print query
                    cursor.execute(query)
                    cnx.commit()
                else:
                    for quantity in cursor:
                        query = "UPDATE USER_PORTFOLIO SET quantity = quantity + '"+check_quantity+"' WHERE username='"+session['username']+"' AND company_name='"+check_symbol+"';";
                        cursor.execute(query)
                        cnx.commit()
            fiveDaysData = []
            start = datetime.today() - timedelta(days=7)
            end = datetime.today() - timedelta(days=1)
            start = start.strftime('%Y-%m-%d')
            end = end.strftime('%Y-%m-%d')
            for i in range(5):
                fiveDaysData.append(0)
            for val in nameValue:
                stock = Share(val.symbol)
                data = stock.get_historical(str(start), str(end))
                count = 0
                for detail in data:
                    value= float(detail['Close'])
                    if value == 0:
                        continue
                    fiveDaysData[count] = fiveDaysData[count] + value * val.quantity
                    count = count + 1
            fiveDaysData.reverse()
            maxValue = max(fiveDaysData) + 100
            minValue = min(fiveDaysData) - 100
            return render_template('engine_recommend_result.html', nameAndValue=nameAndValue, leftAmount=leftAmount, Spent=float(request.form['amount']) - float(leftAmount), fiveDaysData=fiveDaysData, maxValue=maxValue, minValue=minValue, Amount=request.form['amount'])
        return render_template('finance_analysis.html')
    else:
        return render_template('notSignIn.html')
    return render_template('notSignIn.html')

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

def fetchTotalInfo(symbol):
    price, change, perchange = fetchPreMarket(symbol)
    if change == "error":
        return None
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol)
    result = requests.get(url).json()
    real_name = 'unknown'
    for x in result['ResultSet']['Result']:
        if x['symbol'] == symbol:
            real_name=x['name']
            break
    condition = change + ' ' + '(' + str(perchange) + ')'
    temp = Stock(real_name, condition, float(price), symbol)
    return temp

def RRgetQuantity(array, amount):
    print "In rrgetquantity"
    length = len(array)
    print "length is " + str(length)
    index = 0
    count = 0
    amount = float(amount)
    print "amount is " + str(amount)
    while amount > 0 and count < length:
        print "inside while"
        if array[index].single_value <= amount:
            #print "inside if of while"
            count = 0
            amount -= array[index].single_value
            array[index].buy_stock(array[index].quantity + 1)
        else:
            #print "inside else of while"
            count = count + 1
        if index == length - 1:
            index = 0
        else:
            index = index + 1
    for val in array:
        #print "inside for of rr"
        val.value = val.single_value * val.quantity
    print "amount is : " + str(amount)
    print "array in rr is: " 
    
    for i in array:
        print i.printVal()

    return (array, amount)


# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
if __name__ == '__main__':
    print "main called"
    cnx = MySQLdb.connect("portfolio-db.cxbh37qczpuy.us-west-1.rds.amazonaws.com","root", "stock_portfolio" , "stock_portfolio")
    cursor = cnx.cursor()
    query = "SELECT * FROM USER_PORTFOLIO;"
    cursor.execute(query)
    print "db queried" 
    print cursor

    for databas in cursor:
        print databas

    app.run(host='0.0.0.0',debug = True)