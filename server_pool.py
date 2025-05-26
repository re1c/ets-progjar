import socket
import concurrent.futures
import base64
import os

def handle_connection(client_socket, address):
    data = client_socket.recv(1024).decode()
    if data.startswith("LIST"):
        files = os.listdir("server_files")
        client_socket.send("\n".join(files).encode())
    elif data.startswith("GET"):
        filename = data.split()[1]
        with open(f"server_files/{filename}", "rb") as f:
            file_data = base64.b64encode(f.read())
        client_socket.send(file_data)
    elif data.startswith("UPLOAD"):
        filename = data.split()[1]
        file_data = client_socket.recv(5242880)  # Buffer 5MB
        with open(f"server_files/{filename}", "wb") as f:
            f.write(base64.b64decode(file_data))
    client_socket.close()

def start_server(pool_type="thread", max_workers=5):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if pool_type == "process":
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    server.bind(("0.0.0.0", 6000))
    server.listen(10)
    print(f"Server berjalan dengan {pool_type} pool, max_workers={max_workers}")

    executor_class = concurrent.futures.ThreadPoolExecutor if pool_type == "thread" else concurrent.futures.ProcessPoolExecutor
    with executor_class(max_workers=max_workers) as executor:
        while True:
            client_socket, address = server.accept()
            executor.submit(handle_connection, client_socket, address)

if __name__ == "__main__":
    start_server(pool_type="thread", max_workers=5)  # Ganti ke "process" jika diinginkan
