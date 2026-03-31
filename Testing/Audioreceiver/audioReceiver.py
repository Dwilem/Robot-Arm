import socket
import pyaudio

UDP_IP = "192.168.0.101"
UDP_PORT = 6969

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)

print("Receiving audio...")
while True:
    data, addr = sock.recvfrom(2048)
    print(data)
    stream.write(data)
