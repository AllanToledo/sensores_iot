# Trabalho de Sistemas Distribuidos
# Autores: Allan Toledo & João Padilha

import socket
from random import randint
from time import sleep
from datetime import datetime


def clock():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def log(info):
    print(f"{clock()} ..: " + info)

HOST = '192.168.137.181'
PORT = 8000
ID = randint(100,999)

while True:
    try:
        temperatura = randint(20, 40)
        log(f"SENSOR[{ID}]: Enviando {temperatura}")
        
        data = str(f"SENSOR[{ID}]: TEMP = {temperatura}ºC").encode("utf-8")
        size = len(data)
        sensor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        packet = bytearray(1024)
        packet[0] = int(size)
        packet[1:-1] = data
        sensor_socket.sendto(bytes([size]) + data, (HOST, PORT))
        sleep(5)
    except KeyboardInterrupt as e:
        break

if sensor_socket.fileno() > 0:
    sensor_socket.close()

log("Sensor desligado.")
