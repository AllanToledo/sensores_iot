# Trabalho de Sistemas Distribuidos
# Autores: Allan Toledo & João Padilha

import socket as skt
from threading import Thread, Lock
from time import sleep
from datetime import datetime
import argparse


HOST = 'localhost'
SENSOR_PORT = 8000
CLIENT_PORT = 8001

def clock():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def log(info):
    print(f"{clock()} ..: " + info)

def register_log(e: Exception):
    with open("log", "+a") as file:
        file.write(f"{clock()} ..: " + str(e) + "\n")

def is_socket_connected(sock: skt.socket):
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

class Safe:
    def __init__(self):
        self.lock = False

    def getLock(self):
        while self.lock:
            pass
        self.lock = True

    def unlock(self):
        self.lock = False


lock = Lock()
clients_sockets: list[skt.socket] = []
running = True

def connection_clean():
    global lock
    global clients_sockets
    global running
    cnt = 0
    while running:
        sleep(1)
        cnt += 1
        if cnt < 15:
            continue
        cnt = 0

        lock.acquire()
        # limpa a lista de clientes para evitar superlotação com clientes desconectados
        clients_sockets = list(filter(is_socket_connected, clients_sockets))
        lock.release()


def listen_sensors():
    global lock
    global clients_sockets
    global running

    try:
        sensors = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        sensors.bind((HOST, SENSOR_PORT))
        sensors.settimeout(1) # importante, se não o servidor fica escutando para sempre e precisa ser desligado na marra
    except OSError as e:
        running = False
        log("Não foi possível instanciar o socket para sensores.")
        register_log(e)
        
    log(f"Escutando sensores em {HOST}:{SENSOR_PORT}")
    while running:
        try:
            packet, addr = sensors.recvfrom(1024)
            log(f'Sensor conectado: {addr}')
            size = packet[0]
            data = packet[1:size + 1]
            log(data.decode('utf-8'))

            lock.acquire()
        
            # repassa a informação dos sensores para os clientes conectados
            for client in clients_sockets:
                try:
                    client.send(bytes([size]))
                    client.send(data)
                except Exception as e:
                    pass
            
            lock.release()

        except skt.timeout as e:
            continue
        except Exception as e:
            log(e)
            running = False
    
    sensors.close()
    log("Conexão dos sensores fechada.")


def listen_clients():
    global lock
    global clients_sockets
    global running

    try:
        clients = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
        clients.bind((HOST, CLIENT_PORT))
        clients.settimeout(1)
    except OSError as e:
        running = False
        log("Não foi possível instanciar o socket para clientes.")
        register_log(e)

    log(f"Escutando clientes em {HOST}:{CLIENT_PORT}")
    while running:
        try:
            clients.listen()
            client_socket, addr = clients.accept()
            log(f'Cliente conectado: {addr}')

            lock.acquire()
            clients_sockets.append(client_socket)
            lock.release()
            
        except skt.timeout as e:
            continue
        except Exception as e:
            log(e)
            running = False
    
    log("Fechando conexão dos clientes...")
    lock.acquire()
    for client in clients_sockets:
        if client.fileno() > 0:
            client.close()
    clients.close()
    lock.release()
    log("Conexão dos clientes fechada.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--host",         type=str, default="localhost",  required=False, help="Address where the server will start listening")
    parser.add_argument("--sensor_port",  type=int, default=8000,         required=False, help="The port where sensors will send data")
    parser.add_argument("--client_port",  type=int, default=8001,         required=False, help="The port where clients will connect")
    args = parser.parse_args()
    HOST = args.host
    SENSOR_PORT = args.sensor_port
    CLIENT_PORT = args.client_port

    sensors_process = Thread(target=listen_sensors)
    clients_process = Thread(target=listen_clients)
    connection_clean_process = Thread(target=connection_clean)
    clients_process.start()
    sensors_process.start()
    connection_clean_process.start()
    while clients_process.is_alive() or sensors_process.is_alive():
        try:
            sleep(0.001)
        except KeyboardInterrupt:
            log( "Desligando servidor...")
            # Recebeu Ctrl+C do terminal, threads irão sair do loop principal
            running = False
        