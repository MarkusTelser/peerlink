from hashlib import sha1

with open("downloaded.file", "rb") as f:
    data = f.read()

with open("/home/carlos/Downloads/Venom Let There Be Carnage (2021) English 720p CAMRip [NO LOGO] x264 AAC 1.2GB [Themoviesboss].mkv", "rb") as f:
    d = f.read()

print("my file", sha1(data[:2097152]).digest())
print("true file", sha1(d[:2097152]).digest())

for i in range(2097152):
    if d[i] != data[i]:
        print(i)
