from flask import Flask, jsonify, request
app = Flask(__name__)

chain = []
cnt = 0


@app.route('/list', methods=['GET'])
def vote_list():
    return jsonify(chain)


@app.route('/open', methods=['POST'])
def vote_open():
    global cnt
    try:
        data = request.get_json()
        block = {
            'type': 'open',
            'data': {
                'id': str(cnt),
                'question': data['question'],
                'options': data['options']
            }
        }
        cnt += 1
        chain.append(block)
        return jsonify({'status': 'success'})
    except:
        return jsonify({'status': 'fail'})


@app.route('/vote', methods=['POST'])
def vote():
    try:
        data = request.get_json()
        block = {
            'type': 'vote',
            'data': {
                'id': data['id'],
                'vote': data['vote']
            }
        }
        chain.append(block)
        return jsonify({'status': 'success'})
    except:
        return jsonify({'status': 'fail'})


app.run()