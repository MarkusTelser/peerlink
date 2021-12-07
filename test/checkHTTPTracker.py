import os
import bencode
from shutil import copyfile

i = 0
root_path = "/run/media/carlos/FILME/Filme/torrent files/"
for path in os.listdir(root_path):
    try:
        with open(root_path + path, "rb") as f:
            encry = f.read()
        data = bencode.decode(encry)
        if(data.get("announce").split(":")[0]=="udp"):
            print("------------------")
            print(data.get("announce"))
            print(root_path + path)
            copyfile(root_path + path, os.getcwd() + f"/udptorrents/test{i}.torrent") 
            i+=1
    except Exception as e:
        print(e)

