import socket
import sys
import threading

def read_msg(sock_cli):
    while True:
        data = sock_cli.recv(65535)
        if len(data) == 0:
            break
        print(data)

sock_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock_cli.connect(('192.168.0.106', 80))

#kirim username ke server
sock_cli.send(bytes(sys.argv[1], "utf-8"))

#buat thread utk membaca pesan dan jalankan threadnya
thread_cli = threading.Thread(target=read_msg, args=(sock_cli,))
thread_cli.start()

try:
    while True:
        dest = input("Masukan Username tujuan (ketikan bcast untuk braodcast ke semua user): ")
        msg = input("Masukan Pesan: ")

        if msg == "exit":
            sock_cli.close()
            break

        sock_cli.send(bytes("{}|{}".format(dest, msg), "utf-8"))

except KeyboardInterrupt:
    sock_cli.close()
    sys.exit(0)



