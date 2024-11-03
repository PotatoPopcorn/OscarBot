import bluetooth

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

port = 1
server_sock.bind(("", port))
server_sock.listen(1)

print(f"Waiting for a connection on RFCOMM channel {port}")

client_sock, client_info = server_sock.accept()
print("Accepted connection from:", client_info)

try:
    while True:
        data = client_sock.recv(2048)
        if not data:
            break
        print("Received:", data.decode('utf-8'))

except OSError:
    pass

finally:
    client_sock.close()
    server_sock.close()

