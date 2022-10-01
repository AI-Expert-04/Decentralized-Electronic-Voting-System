chain = []

block1 = {
    'type': 'open',
    'data': {
        'id': '투표 ID',
        'question': '투표 질문',
        'options': ['투표 항목1', '투표 항목2', '투표 항목3']
    }
}

chain.append(block1)

block2 = {
    'type': 'vote',
    'data': {
        'id': '투표 ID',
        'vote': '투표 항목1'
    }
}

chain.append(block2)
print(chain)
