# from pyftpdlib import servers
# from pyftpdlib.handlers import FTPHandler

# # Konfigurasi server FTP
# server_address = '192.168.1.13'
# server_port = 21
# username = 'vin'
# password = '1234'

# # Membuat handler FTP
# handler = FTPHandler
# handler.authorizer.add_user(username, password, ".", perm='elradfmw')

# # Membuat server FTP
# server = servers.FTPServer((server_address, server_port), handler)

# # Menjalankan server FTP
# server.serve_forever()


from ftplib import FTP
import sys
import time
import os
import struct

print("\nWelcome to the FTP server.\n\nTo get started, connect a client.")

# Konfigurasi server FTP
FTP_IP = "192.168.1.13"  # Alamat server FTP
FTP_PORT = 21  # Port server FTP
BUFFER_SIZE = 1024  # Ukuran buffer standar
ftp = FTP()

ftp.connect(FTP_IP, FTP_PORT)
ftp.login()
print("\nConnected to FTP server: {}:{}".format(FTP_IP, FTP_PORT))


def upld():
    # Kirim pesan setelah server siap menerima detail file
    conn.send(b"1")
    # Terima panjang nama file, kemudian nama file
    file_name_size = struct.unpack("h", conn.recv(2))[0]
    file_name = conn.recv(file_name_size).decode()
    # Kirim pesan untuk memberi tahu klien bahwa server siap menerima konten dokumen
    conn.send(b"1")
    # Terima ukuran file
    file_size = struct.unpack("i", conn.recv(4))[0]
    # Inisialisasi dan masuk ke dalam loop untuk menerima konten file
    start_time = time.time()
    output_file = open(file_name, "wb")
    # Ini melacak berapa byte yang telah kita terima, sehingga kami tahu kapan harus menghentikan loop
    bytes_received = 0
    print("\nReceiving...")
    while bytes_received < file_size:
        l = conn.recv(BUFFER_SIZE)
        output_file.write(l)
        bytes_received += len(l)
    output_file.close()
    print("\nReceived file: {}".format(file_name))
    # Kirim detail kinerja unggah
    conn.send(struct.pack("f", time.time() - start_time))
    conn.send(struct.pack("i", file_size))
    return


def list_files():
    print("Listing files...")
    # Dapatkan daftar file dalam direktori
    listing = ftp.nlst()
    # Kirim jumlah file, sehingga klien tahu apa yang diharapkan (dan menghindari beberapa kesalahan)
    conn.send(struct.pack("i", len(listing)))
    total_directory_size = 0
    # Kirim nama file dan ukurannya sambil menjumlahkan ukuran direktori
    for i in listing:
        # Ukuran nama file
        conn.send(struct.pack("i", sys.getsizeof(i)))
        # Nama file
        conn.send(i.encode())
        # Ukuran konten file
        file_size = ftp.size(i)
        conn.send(struct.pack("i", file_size))
        total_directory_size += file_size
        # Pastikan klien dan server disinkronkan
        conn.recv(BUFFER_SIZE)
    # Jumlah ukuran file dalam direktori
    conn.send(struct.pack("i", total_directory_size))
    # Pengecekan akhir
    conn.recv(BUFFER_SIZE)
    print("Successfully sent file listing")
    return


def dwld():
    conn.send(b"1")
    file_name_length = struct.unpack("h", conn.recv(2))[0]
    print(file_name_length)
    file_name = conn.recv(file_name_length).decode()
    print(file_name)
    if file_name in ftp.nlst():
        # Jika file ada, kirim ukuran file
        file_size = ftp.size(file_name)
        conn.send(struct.pack("i", file_size))
    else:
        # Jika file tidak ada, kirim kode error
        print("File name not valid")
        conn.send(struct.pack("i", -1))
        return
    # Tunggu persetujuan untuk mengirim file
    conn.recv(BUFFER_SIZE)
    # Masuk ke dalam loop untuk mengirim file
    start_time = time.time()
    print("Sending file...")
    content = open(file_name, "rb")
    # Lagi, pecah menjadi bagian yang ditentukan oleh BUFFER_SIZE
    l = content.read(BUFFER_SIZE)
    while l:
        conn.send(l)
        l = content.read(BUFFER_SIZE)
    content.close()
    # Dapatkan persetujuan dari klien, lalu kirim detail unduhan
    conn.recv(BUFFER_SIZE)
    conn.send(struct.pack("f", time.time() - start_time))
    return


def delf():
    # Kirim persetujuan
    conn.send(b"1")
    # Dapatkan detail file
    file_name_length = struct.unpack("h", conn.recv(2))[0]
    file_name = conn.recv(file_name_length).decode()
    # Periksa apakah file ada
    if file_name in ftp.nlst():
        conn.send(struct.pack("i", 1))
    else:
        # Jika file tidak ada
        conn.send(struct.pack("i", -1))
        return
    # Tunggu konfirmasi penghapusan
    confirm_delete = conn.recv(BUFFER_SIZE).decode()
    if confirm_delete == "Y":
        try:
            # Hapus file
            ftp.delete(file_name)
            conn.send(struct.pack("i", 1))
        except:
            # Tidak dapat menghapus file
            print("Failed to delete {}".format(file_name))
            conn.send(struct.pack("i", -1))
    else:
        # Pengguna membatalkan penghapusan
        # Server mungkin menerima "N", tetapi else digunakan sebagai pengaman penangkapan kesalahan
        print("Delete abandoned by client!")
        return


def quit_ftp():
    # Kirim konfirmasi keluar
    conn.send(b"1")
    # Tutup dan restart server
    conn.close()
    ftp.quit()
    os.execl(sys.executable, sys.executable, *sys.argv)


while True:
    # Masuk ke dalam loop while untuk menerima perintah dari klien
    print("\n\nWaiting for instruction")
    data = conn.recv(BUFFER_SIZE).decode()
    print("\nReceived instruction: {}".format(data))
    # Periksa perintah dan tanggapi dengan benar
    if data == "UPLD":
        upld()
    elif data == "LIST":
        list_files()
    elif data == "DWLD":
        dwld()
    elif data == "DELF":
        delf()
    elif data == "QUIT":
        quit_ftp()
    # Reset data untuk melooping
    data = None
