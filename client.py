# Trabalho de Sistemas Distribuidos
# Autores: Allan Toledo & João Padilha

import socket
from datetime import datetime


def clock():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def log(info):
    print(f"{clock()} ..: " + info)

    
# HOST = '127.0.0.1'
HOST = '192.168.137.181'
PORT = 8001

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def is_socket_connected(sock: socket.socket):
    try:
        sock.setblocking(False)
        data = sock.recv(1, socket.MSG_PEEK)
        return False if data == b'' else True
    except BlockingIOError:
        sock.setblocking(True)
        return True
    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
        return False
    finally:
        sock.setblocking(True)

try:
    log(f"Connectando em [{HOST}]...")
    client_socket.settimeout(30)
    client_socket.connect((HOST, PORT))
    log(f"Conexão realizada com sucesso!")
    log(f"Escutando dados:")
    client_socket.settimeout(1)
    while is_socket_connected(client_socket):
        try:
            first_bytes = client_socket.recv(1)
            if len(first_bytes) > 0:
                size = first_bytes[0]
                data = client_socket.recv(size)
                log(data.decode('utf-8'))
        except TimeoutError as e:
            continue
        except KeyboardInterrupt as e:
            log("Desligando...")
            client_socket.close()
            break

    log("Conexão fechada.")
except TimeoutError as e:
    log("Não foi possível conectar no servidor.")
except ConnectionRefusedError as e:
    log("Servidor está offline.")


