# write 20 byte file
with open("test.mov", "wb") as f:
    f.write(b'\x00'*11)

with open("test.mov","r+b") as f:
    f.seek(5)
    f.write(b'\x11')
