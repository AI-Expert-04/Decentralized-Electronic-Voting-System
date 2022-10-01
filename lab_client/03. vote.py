import requests, json

headers = {'Content-Type': 'application/json'}

data = {
    'id': '0',
    'vote': 'A1'
}

res = requests.post(
    'http://127.0.0.1:5000/vote',
    data=json.dumps(data),
    headers=headers)
print(res.text)
