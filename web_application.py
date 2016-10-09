from flask import Flask, render_template, send_from_directory, session
app = Flask(__name__)

# controllers
#@app.route('/favicon.ico')
#def favicon():
#    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/logout")
def logout():
    session['logged_in'] = False;
    return render_template('index.html')

@app.route("/login_signin")
def login_signin():
    session['logged_in'] = True;
    return render_template('index.html')

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
if __name__ == '__main__':
    app.run()