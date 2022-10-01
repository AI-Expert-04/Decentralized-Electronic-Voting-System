from flask import Flask, jsonify, request
app = Flask(__name__)


@app.route('/api1', methods=['GET'])
def f1():
    return jsonify({'status': 'success'})


@app.route('/api2', methods=['POST'])
def f2():
    data = request.get_json()
    return jsonify(data)


app.run()