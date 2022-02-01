from src.backend.metadata.Bencoder import bencode
from collections import OrderedDict

print('-'*20)
print(bencode('haus'))
print(bencode(b'haus'))
print(bencode(''))
print(bencode(b''))

print('-'*20)
print(bencode(13213))
print(bencode(-12))
print(bencode(0))
print(bencode(-0))
print(bencode(-12))

print('-'*20)
print(bencode([]))
print(bencode(()))
print(bencode(['haus',b'checkitout',12312]))
print(bencode(('haus',b'checkitout',12312)))
print(bencode([1,2,[[1]]]))
print(bencode([[[[]]]]))

print('-'*20)
print(bencode({'test':12312321,'hello_guys':b'test'}))
d = OrderedDict()
print(bencode(d))
