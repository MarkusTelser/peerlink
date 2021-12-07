from src.backend.metadata.Bencoder import encode, decode
import os

path = "data/all/solo.torrent"

def decode_encode(path):
    with open(path, "rb") as f:
        data = f.read()

    dec = decode(data)
    enc = encode(dec)
    
    if enc == data:
        print("success")
    else:
        print("--fail--")
        print(path)
        for i, d in enumerate(enc):
            if d != data[i]:
                print("real", chr(data[i]), "wrong", chr(d))
                print("real", data[i - 10:i + 50])
                print("wrong", enc[i - 10: i + 50])
                break


for file in os.listdir("data/all"):
    decode_encode(os.path.join("data/all", file))

