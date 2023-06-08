import socket
import os
import struct
import time

TCP_IP = "192.168.6.230"  # Alamat IP server
TCP_PORT = 1456  # Port server
BUFFER_SIZE = 1024  # Ukuran buffer

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
print("Server is running and listening...")

while True:
    conn, addr = s.accept()
    print("Connection address:", addr)

    # Menerima permintaan dari client
    request = conn.recv(BUFFER_SIZE)
    if request == b"UPLD":
        print("Upload request received.")

        # Mengirimkan konfirmasi ke client
        conn.send(b"OK")

        # Menerima ukuran nama file
        file_name_size = struct.unpack("h", conn.recv(2))[0]

        # Menerima nama file
        file_name = conn.recv(file_name_size).decode()
        print("Received file name:", file_name)

        # Mengirimkan konfirmasi ke client
        conn.send(b"OK")

        # Menerima ukuran file
        file_size = struct.unpack("i", conn.recv(4))[0]
        print("Received file size:", file_size, "bytes")

        # Menyiapkan path penyimpanan file
        save_directory = "C:\\Users\\Lenovo\\Downloads\\week14\\week14\\gambar"  # Ganti dengan path yang sesuai
        save_path = os.path.join(save_directory, file_name)

        # Menerima file dan menyimpannya
        with open(save_path, "wb") as file:
            print("Receiving file...")
            start_time = time.time()
            remaining_size = file_size
            while remaining_size > 0:
                data = conn.recv(min(BUFFER_SIZE, remaining_size))
                if not data:
                    break
                file.write(data)
                remaining_size -= len(data)
                end_time = time.time()
        print("File received and saved successfully.")

        # Menghitung dan mengirimkan detail performa upload ke client
        upload_time = end_time - start_time # Ganti dengan waktu upload yang sesuai
        upload_size = file_size
        conn.send(struct.pack("f", upload_time))
        conn.send(struct.pack("i", upload_size))

        # Mencetak daftar file dalam direktori penyimpanan
        file_list = os.listdir(save_directory)
        print("File list in save directory:")
        for file in file_list:
            print(file)

    conn.close()
