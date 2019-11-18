from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO,emit 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/received', methods=['GET', 'POST'])
def received():
	print("Received {}".format(request.form['msg']))
	received(request.form['msg'])
	return jsonify({'data': 'success'})

def received(msg):
	#EMITTING TO RECEIVED SOCKET
	emit('received', msg, broadcast=True, namespace='/received')

socketio.run(app,host="0.0.0.0",debug=True)