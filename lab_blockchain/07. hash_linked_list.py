import hashlib


def get_block_hash(block):
    data = dict()
    data['type'] = block['transaction']['type']
    data['data'] = sorted(block['transaction']['data'].copy().items())
    data['previous_hash'] = block['previous_hash']
    data = sorted(data.items())
    return hashlib.sha256(str(data).encode()).hexdigest()


genesis_block = {
    'transaction': {
        'type': 'genesis',
        'data': dict()
    },
    'previous_hash': None
}
genesis_block['hash'] = get_block_hash(genesis_block)

chain = [genesis_block]

block1 = {
    'transaction': {
        'type': 'open',
        'data': {
            'id': '투표 ID',
            'question': '투표 질문',
            'options': ['투표 항목1', '투표 항목2', '투표 항목3']
        }
    },
    'previous_hash': chain[-1]['hash']
}
block1['hash'] = get_block_hash(block1)
print(block1)

chain.append(block1)

block2 = {
    'transaction': {
        'type': 'vote',
        'data': {
            'id': '투표 ID',
            'vote': '투표 항목2'
        }
    },
    'previous_hash': chain[-1]['hash']
}
block2['hash'] = get_block_hash(block2)
print(block2)

chain.append(block2)
print(chain)