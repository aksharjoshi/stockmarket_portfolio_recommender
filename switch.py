from flask import Flask, jsonify
from flask import request
import time
app = Flask(__name__)
control = 0
start = time.time()
energy = 0.16;
total = 0;


@app.route('/switch_control/')
def switch_control():
	global control
	global start
	global total
	if control == 0:
		control = 1
		start = time.time()
	else:
		control = 0
        end = time.time()
        total = total + (end - start) * energy
	if control == 0:
		list = [
        {'param': 'status', 'val': 0},
        {'param': 'energy', 'val': total}
    ]
		return jsonify(result = list)
	else:
		list = [
        {'param': 'status', 'val': 1}
    ]
    	return jsonify(result = list)

@app.route('/switch_reflect/')
def switch_reflect():
	status = request.args.get('status', '')
	global control
	global start
	global total
	if status == '0' and control == 1:
		control = 0
		end = time.time()
		total = total + (end - start) * energy
	elif status == '1' and control == 0:
		control = 1
		start = time.time
	return 'The switch status has been updated' 

@app.route('/')
def hello():
	list = [
        {'param': 'message', 'val': 'connected', 'status': control}
    ]
	return jsonify(result = list)

@app.route('/check_powercost')
def power_energy():
	list = [
        {'param': 'energy', 'val': total}
    ]
	return jsonify(result = list)




if __name__ == '__main__':
    app.run(debug = True)