import socket
import sys
import threading
import os
import ntpath

def read_msg(sock_cli):
    while True:
        data = sock_cli.recv(65535)
        if len(data) == 0:
            break
        datatype, message = data.split(b"|", 1)
        datatype = datatype.decode("utf-8")
        if datatype == "message":
            message = message.decode("utf-8")
            print(message)
        elif datatype == "file":
            sender, filename, filesize, filedata = message.split(b'|', 3)
            sender = sender.decode('utf-8')
            print("file received from", sender)
            filename = filename.decode('utf-8')
            filename = ntpath.basename(filename)
            filesize = int(filesize.decode('utf-8'))
            while len(filedata) < filesize:
                if filesize - len(filedata) > 65536:
                    filedata += sock_cli.recv(65536)
                else:
                    filedata += sock_cli.recv(filesize - len(filedata))
                    break
            with open(filename, 'wb') as f:
                f.write(filedata)

sock_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock_cli.connect(('192.168.0.106', 80))

#kirim username ke server
sock_cli.send(bytes(sys.argv[1], "utf-8"))

#buat thread utk membaca pesan dan jalankan threadnya
thread_cli = threading.Thread(target=read_msg, args=(sock_cli,))
thread_cli.start()

try:
    while True:
        dest = input("Instant Messanger : \n1. message <username> <message> (kirim message biasa)\n2. bcast <message> (kirim broadcast)\n3. sendfile <username> <filepath> (kirim file)\n4. exit (keluar)\n")
        msg = dest.split(" ", 1)

        if msg[0] == "exit":
            sock_cli.close()
            break
        elif msg[0] == "message":
            username, message = msg[1].split(" ", 1)
            sock_cli.send(f"{username}|{message}".encode("utf-8"))
        elif msg[0] == "bcast":
            sock_cli.send(f"bcast|{msg[1]}".encode("utf-8"))
        elif msg[0] == "sendfile":
            username, filepath = msg[1].split(" ", 1)
            size = os.path.getsize(filepath)
            print("sending ", filepath, " to ", username)
            filedata = f'sendfile|{username}|{filepath}|{size}|'.encode('utf-8')
            with open(filepath, 'rb') as f:
                filedata += f.read()
            sock_cli.sendall(filedata)

except KeyboardInterrupt:
    sock_cli.close()
    sys.exit(0)



