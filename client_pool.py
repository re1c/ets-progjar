import socket
import concurrent.futures
import base64
import os

def list_files():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 6000))
    s.send("LIST".encode())
    data = s.recv(1024).decode()
    print("Daftar file di server:\n", data)
    s.close()

def download_file(filename):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 6000))
    s.send(f"GET {filename}".encode())
    data = s.recv(5242880)  # Buffer 5MB
    with open(f"downloaded_{filename}", "wb") as f:
        f.write(base64.b64decode(data))
    print(f"Berhasil mendownload {filename}")
    s.close()

def upload_file(filename):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 6000))
    with open(filename, "rb") as f:
        file_data = base64.b64encode(f.read())
    s.send(f"UPLOAD {filename}".encode())
    s.send(file_data)
    print(f"Berhasil mengupload {filename}")
    s.close()

def run_tasks(pool_type="thread", max_workers=5):
    tasks = [
        ("list", None),
        ("download", "testfile.txt"),
        ("upload", "sample.txt")
    ]
    executor_class = concurrent.futures.ThreadPoolExecutor if pool_type == "thread" else concurrent.futures.ProcessPoolExecutor
    with executor_class(max_workers=max_workers) as executor:
        for task_type, param in tasks:
            if task_type == "list":
                executor.submit(list_files)
            elif task_type == "download":
                executor.submit(download_file, param)
            elif task_type == "upload":
                executor.submit(upload_file, param)

if __name__ == "__main__":
    run_tasks(pool_type="thread", max_workers=5)
