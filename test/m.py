from src.backend.metadata.Bencoder import encode
from collections import OrderedDict

print('-'*20)
print(encode('haus'))
print(encode(b'haus'))
print(encode(''))
print(encode(b''))

print('-'*20)
print(encode(13213))
print(encode(-12))
print(encode(0))
print(encode(-0))
print(encode(-12))

print('-'*20)
print(encode([]))
print(encode(()))
print(encode(['haus',b'checkitout',12312]))
print(encode(('haus',b'checkitout',12312)))
print(encode([1,2,[[1]]]))
print(encode([[[[]]]]))

print('-'*20)
print(encode({'test':12312321,'hello_guys':b'test'}))
d = OrderedDict()
print(encode(d))
