import socket
import sys
import threading

def read_msg(clients, sock_cli, addr_cli, username_cli):
    while True:
        data = sock_cli.recv(65535)
        if len(data) == 0:
            break

        #parsing pesannya
        dest, msg = data.split(b"|", 1)
        dest = dest.decode("utf-8")

        #kirim data ke semua client
        if dest == "bcast":
            msg = msg.decode("utf-8")
            _msg = f"<{username_cli}>: {msg}"
            send_broadcast(clients, _msg, addr_cli)
        elif dest == "sendfile":
            dest_username, filename, size, filedata = msg.split(b'|', 3)
            dest_username = dest_username.decode("utf-8")
            filename = filename.decode("utf-8")
            size = int(size.decode("utf-8"))

            while len(filedata) < size:
                if size-len(filedata) > 65536:
                    filedata += sock_cli.recv(65536)
                else:
                    filedata += sock_cli.recv(size - len(filedata))
                    break
            
            dest_sock_cli = clients[dest_username][0]
            send_file(dest_sock_cli, filename, size, filedata, dest_username)
        else:
            msg = msg.decode("utf-8")
            _msg = f"<{username_cli}>: {msg}"
            dest_sock_cli = clients[dest][0]
            send_msg(dest_sock_cli, _msg)
    sock_cli.close()
    print("connection closed", addr_cli)

def send_file(sock_cli, filename, size, filedata, username):
    file = f'file|{username}|{filename}|{size}|'.encode('utf-8')
    file += filedata
    sock_cli.sendall(file)

def send_broadcast(clients, data, sender_addr_cli):
    for sock_cli, addr_cli, _ in clients.values():
        if not (sender_addr_cli[0] == addr_cli[0] and sender_addr_cli[1] == addr_cli[1]):
            send_msg(sock_cli, data)

def send_msg(sock_cli, data):
    message = f'message|{data}'
    sock_cli.send(bytes(message, "utf-8"))

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
