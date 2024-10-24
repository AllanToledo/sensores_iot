# Trabalho de Sistemas Distribuidos
# Autores: Allan Toledo & João Padilha

import socket as skt
from threading import Thread
from time import sleep
from datetime import datetime


HOST = '192.168.137.181'
PORT_SENSORS = 8000
PORT_CLIENTS = 8001

def clock():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def log(info):
    print(f"{clock()} ..: " + info)

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


clients_sockets: list[skt.socket] = []
running = True

def listen_sensors():
    sensors = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
    sensors.bind((HOST, PORT_SENSORS))
    sensors.settimeout(1)
    log("Escutando sensores:")
    global clients_sockets
    global running
    while running:
        try:
            packet, addr = sensors.recvfrom(1024)
            log(f'Sensor conectado: {addr}')
            size = packet[0]
            data = packet[1:size + 1]
            log(data.decode('utf-8'))

            need_cleaning = False
            for client in clients_sockets:
                if not is_socket_connected(client):
                    need_cleaning = True
                    continue
                client.send(bytes([size]))
                client.send(data)
            if need_cleaning:
                clients_sockets = list(filter(is_socket_connected, clients_sockets))
        except skt.timeout as e:
            continue
        except Exception as e:
            log(e)
            running = False
    
    sensors.close()
    log("Conexão dos sensores fechada.")


def listen_clients():
    clients = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
    clients.bind((HOST, PORT_CLIENTS))
    clients.settimeout(1)
    log("Escutando clientes:")
    global clients_sockets
    global running
    while running:
        try:
            clients.listen()
            client_socket, addr = clients.accept()
            log(f'Cliente conectado: {addr}')
            clients_sockets.append(client_socket)
            
        except skt.timeout as e:
            continue
        except Exception as e:
            log(e)
            running = False
    
    log("Fechando conexão dos clientes...")
    for client in clients_sockets:
        if client.fileno() > 0:
            client.close()
    clients.close()
    log("Conexão dos clientes fechada.")


if __name__ == "__main__":
    sensors_process = Thread(target=listen_sensors)
    clients_process = Thread(target=listen_clients)
    clients_process.start()
    sensors_process.start()
    while clients_process.is_alive() or sensors_process.is_alive():
        try:
            sleep(0.001)
        except KeyboardInterrupt:
            log( "Desligando servidor...")
            running = False
        