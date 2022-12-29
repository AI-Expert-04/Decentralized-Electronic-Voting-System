import hashlib

difficulty = 5

data = 'data'
nonce = 0

while True:
    data_with_nonce = (str(data) + str(nonce)).encode()
    data_hash = hashlib.sha256(str(data_with_nonce).encode()).hexdigest()
    if data_hash[:difficulty] == '0' * difficulty:
        print(nonce)
        print(data_hash)
        break
    else:
        nonce += 1