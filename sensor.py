# Trabalho de Sistemas Distribuidos
# Autores: Allan Toledo & João Padilha

import socket as skt
from random import randint
from time import sleep
from datetime import datetime
import argparse


def clock():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def log(info):
    print(f"{clock()} ..: " + info)

def is_socket_connected(sock: skt.socket):
    if sock.fileno() <= 0:
        return False
    try:
        sock.setblocking(False)
        data = sock.recv(1, skt.MSG_PEEK)
        return False if data == b'' else True
    except BlockingIOError:
        sock.setblocking(True)
        return True
    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
        return False
    finally:
        sock.setblocking(True)

HOST = 'localhost'
PORT = 8000
ID = randint(100,999)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--host", type=str, default="localhost",       required=False, help="Address where the sensor will connect")
    parser.add_argument("--port", type=int, default=8000,              required=False, help="The port where the sensor will send data")
    parser.add_argument("--id",   type=int, default=randint(100, 999), required=False, help="Identifier of the sensor")
    args = parser.parse_args()
    HOST = args.host
    PORT = args.port
    ID = args.id


    sensor_socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)

    while True:
        try:
            temperatura = randint(20, 40)
            log(f"SENSOR[{ID}]: Enviando {temperatura}")
            
            data = str(f"SENSOR[{ID}]: TEMP = {temperatura}ºC").encode("utf-8")
            size = len(data)
            sensor_socket.sendto(bytes([size]) + data, (HOST, PORT))
            
            sleep(5)
        except KeyboardInterrupt as e:
            break
    
    sensor_socket.close()

    log("Sensor desligado.")
