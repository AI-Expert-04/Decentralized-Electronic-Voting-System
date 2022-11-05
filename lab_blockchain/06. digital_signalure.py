from ecdsa import SigningKey as sk
import hashlib as hs

private_key = sk.generate()
public_key = private_key.get_verifying_key()
wallet_address = hs.sha256(public_key.to_string()).hexdigest()

data = 'data'

signature = private_key.sign(data.encode())
print(signature)

try:
    public_key.verify(signature, data.encode())
    print('일치')

except:
    print('불일치')

try:
    public_key.verify('moified_data'.encode(), data.encode())
    print('일치1')

except:
    print('불일치1')

# 이 주소를 벤! 악의적으로 변조를하면