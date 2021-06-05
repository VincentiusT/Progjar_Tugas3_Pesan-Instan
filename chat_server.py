import socket
import sys
import threading

def read_msg(clients, sock_cli, addr_cli, username_cli):
    while True:
        data = sock_cli.recv(65535)
        if len(data) == 0:
            break

        #parsing pesannya
        dest, msg = data.decode("utf-8").split("|")
        msg = "<{}>: {}".format(username_cli, msg)

        #kirim data ke semua client
        if dest == "bcast":
            send_broadcast(clients, msg, addr_cli)
        else:
            dest_sock_cli = clients[dest][0]
            send_msg(dest_sock_cli, msg)
        print(data)
    sock_cli.close()
    print("connection closed", addr_cli)

def send_broadcast(clients, data, sender_addr_cli):
    for sock_cli, addr_cli, _ in clients.values():
        if not (sender_addr_cli[0] == addr_cli[0] and sender_addr_cli[1] == addr_cli[1]):
            send_msg(sock_cli, data)

def send_msg(sock_cli, data):
    sock_cli.send(bytes(data, "utf-8"))

server_address = ('192.168.0.106', 80)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(server_address)
server_socket.listen(5)

#buat dictionary utk menyimpan informasi
clients = {}

try:
    while True:
        sock_cli, addr_cli = server_socket.accept()

        #baca username client
        username_cli = sock_cli.recv(65535).decode("utf-8")
        print(username_cli, "joined")

        #buat thread
        thread_cli = threading.Thread(target=read_msg, args=(clients, sock_cli, addr_cli, username_cli))
        thread_cli.start()

        #simpan informasi client ke dictionary
        clients[username_cli] = (sock_cli, addr_cli, thread_cli)

except KeyboardInterrupt:
    server_socket.close()
    sys.exit(0)
