# Trabalho de Sistemas Distribuidos
# Autores: Allan Toledo & João Padilha

import socket
from datetime import datetime
import argparse


def clock():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def log(info):
    print(f"{clock()} ..: " + info)

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="localhost", required=False, help="Address where the client will connect")
    parser.add_argument("--port", type=int, default=8001,        required=False, help="The port where the client will connect")
    args = parser.parse_args()
    HOST = args.host
    PORT = args.port


    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        log(f"Connectando em [{HOST}]...")
        client_socket.settimeout(30)
        client_socket.connect((HOST, PORT))
        client_socket.settimeout(1)

        log("Conexão realizada com sucesso!")
        log("Escutando dados:")
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

        log("Conexão fechada.")
    except TimeoutError as e:
        log("Não foi possível conectar no servidor.")
    except ConnectionRefusedError as e:
        log("Servidor está offline.")
    finally:
        client_socket.close()

