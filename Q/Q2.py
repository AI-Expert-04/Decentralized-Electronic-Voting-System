from flask import Flask, jsonify
import requests, json

headers = {'Content-Type': 'application/json'}
Chain = []

while True:
    CUI = int(input('1. 블록 체인 조회\n2. 투표 생성\n3. 투표\n=>>'))

    if CUI == 1:
        res = requests.get('http://127.0.0.1:5000/list')
        print(res.text)

    elif CUI == 2:
        data = {
        }
        # id, vote = data.keys()
        question = input('질문: ')
        data.update({'question': question})
        options = int(input('선택지 1: '))
        data.update({'options': [options]})
        options2 = int(input('선택지 2: '))
        data['options'].append(options2)
        options3 = int(input('선택지 3: '))
        data['options'].append(options3)
        print(data)
        res = requests.post('http://127.0.0.1:5000/open', data=json.dumps(data), headers=headers)
        print(res.text)

    elif CUI == 3:
        data = {
            'id': '0',
            'vote': 'A1'
        }
        ID = int(input('투표 ID: '))
        data.update({'id': ID})
        Vote = input('투표: ')
        data.update({'vote': Vote})
        res = requests.post(
            'http://127.0.0.1:5000/vote',
            data=json.dumps(data),
            headers=headers)
        print(data)
        print(res.text)

    elif CUI == 4:
        break
