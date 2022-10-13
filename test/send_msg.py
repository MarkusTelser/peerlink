import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(('127.0.0.1', 6900))
sock.sendall(b'dsjlkafdsakjfjdsalkfsa')