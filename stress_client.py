import socket
import concurrent.futures
import time
import os
import base64

def generate_file(size_mb, filename):
    with open(filename, "wb") as f:
        f.write(os.urandom(size_mb * 1024 * 1024))

def download_task(filename):
    start_time = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 6000))
    s.send(f"GET {filename}".encode())
    data = s.recv(5242880)
    s.close()
    end_time = time.time()
    size = os.path.getsize(filename)
    return end_time - start_time, size / (end_time - start_time), True

def upload_task(filename):
    start_time = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 6000))
    with open(filename, "rb") as f:
        file_data = base64.b64encode(f.read())
    s.send(f"UPLOAD {filename}".encode())
    s.send(file_data)
    s.close()
    end_time = time.time()
    size = os.path.getsize(filename)
    return end_time - start_time, size / (end_time - start_time), True

def run_stress_test(operation, size_mb, client_workers, server_workers, pool_type):
    generate_file(size_mb, f"test_{size_mb}MB.txt")
    executor_class = concurrent.futures.ThreadPoolExecutor if pool_type == "thread" else concurrent.futures.ProcessPoolExecutor
    results = []
    with executor_class(max_workers=client_workers) as executor:
        if operation == "download":
            futures = [executor.submit(download_task, f"test_{size_mb}MB.txt") for _ in range(client_workers)]
        else:
            futures = [executor.submit(upload_task, f"test_{size_mb}MB.txt") for _ in range(client_workers)]
        results = [f.result() for f in futures]
    total_time = sum(r[0] for r in results) / len(results)
    throughput = sum(r[1] for r in results) / len(results)
    success = sum(1 for r in results if r[2])
    return total_time, throughput, success, client_workers - success

if __name__ == "__main__":
    operations = ["download", "upload"]
    sizes = [10, 50, 100]
    workers = [1, 5, 50]
    for op in operations:
        for size in sizes:
            for cw in workers:
                for sw in workers:
                    time_taken, throughput, success, failure = run_stress_test(op, size, cw, sw, "thread")
                    print(f"{op}, {size}MB, {cw} clients, {sw} servers: {time_taken}s, {throughput} bytes/s, {success}/{failure}")
