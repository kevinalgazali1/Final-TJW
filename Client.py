# from ftplib import FTP

# # Konfigurasi server FTP
# FTP_HOST = "192.168.1.13"  # Alamat server FTP
# FTP_PORT = 21  # Port server FTP
# FTP_USER = "vin"  # Nama pengguna FTP
# FTP_PASS = "1234"  # Kata sandi pengguna FTP

# def upload_file(file_name):
#     # Upload file ke server FTP
#     try:
#         ftp = FTP()
#         ftp.connect(FTP_HOST, FTP_PORT)
#         ftp.login(FTP_USER, FTP_PASS)
#         ftp.storbinary("STOR " + file_name, open(file_name, "rb"))
#         ftp.quit()
#         print("File uploaded successfully.")
#     except Exception as e:
#         print("Error uploading file:", str(e))

# def list_files():
#     # Mendapatkan daftar file yang tersedia di server FTP
#     try:
#         ftp = FTP()
#         ftp.connect(FTP_HOST, FTP_PORT)
#         ftp.login(FTP_USER, FTP_PASS)
#         file_list = ftp.nlst()
#         for file_name in file_list:
#             print(file_name)
#         ftp.quit()
#     except Exception as e:
#         print("Error retrieving file list:", str(e))

# def download_file(file_name):
#     # Download file dari server FTP
#     try:
#         ftp = FTP()
#         ftp.connect(FTP_HOST, FTP_PORT)
#         ftp.login(FTP_USER, FTP_PASS)
#         ftp.retrbinary("RETR " + file_name, open(file_name, "wb").write)
#         ftp.quit()
#         print("File downloaded successfully.")
#     except Exception as e:
#         print("Error downloading file:", str(e))

# def delete_file(file_name):
#     # Menghapus file dari server FTP
#     try:
#         ftp = FTP()
#         ftp.connect(FTP_HOST, FTP_PORT)
#         ftp.login(FTP_USER, FTP_PASS)
#         ftp.delete(file_name)
#         ftp.quit()
#         print("File deleted successfully.")
#     except Exception as e:
#         print("Error deleting file:", str(e))

# # Menjalankan FTP client
# print("\nWelcome to the FTP client.")
# print("Available commands:")
# print("UPLOAD file_path  : Upload file to FTP server")
# print("LIST              : List files on FTP server")
# print("DOWNLOAD file     : Download file from FTP server")
# print("DELETE file       : Delete file from FTP server")
# print("QUIT              : Exit FTP client")

# while True:
#     command = input("\nEnter a command: ").split()
#     if not command:
#         continue

#     if command[0].upper() == "UPLOAD":
#         if len(command) > 1:
#             upload_file(command[1])
#         else:
#             print("Please provide a file path.")
#     elif command[0].upper() == "LIST":
#         list_files()
#     elif command[0].upper() == "DOWNLOAD":
#         if len(command) > 1:
#             download_file(command[1])
#         else:
#             print("Please provide a file name.")
#     elif command[0].upper() == "DELETE":
#         if len(command) > 1:
#             delete_file(command[1])
#         else:
#             print("Please provide a file name.")
#     elif command[0].upper() == "QUIT":
#         break
#     else:
#         print("Command not recognized; please try again.")

import PySimpleGUI as sg
from flask import Flask, request, render_template, redirect, send_file, make_response
from ftplib import FTP
from io import BytesIO
import threading

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Konfigurasi FTP
ftp_host = "192.168.1.14"
ftp_user = 'alqa'
ftp_password = 'alqa'

# Menggunakan lock untuk mengakses variabel bersama
lock = threading.Lock()

# Fungsi untuk menghubungkan ke FTP
def get_ftp_connection():
    ftp = FTP(ftp_host)
    ftp.login(user=ftp_user, passwd=ftp_password)
    return ftp

# Fungsi untuk mengunggah file ke server FTP
def upload_file(file):
    try:
        with get_ftp_connection() as ftp:
            # Mengirim file langsung dari objek FileStorage
            ftp.storbinary('STOR {}'.format(file.filename), file.stream)
        
        with lock:
            file_list = get_file_list()
            file_list.append(file.filename)
    except Exception as e:
        # Tangani kesalahan jika terjadi
        print(f"Error during file upload: {str(e)}")

# Fungsi untuk mengunduh file dari server FTP
def download_file(file_name):
    try:
        with get_ftp_connection() as ftp:
            # Mengunduh file langsung ke objek BytesIO
            file_data = BytesIO()
            ftp.retrbinary('RETR {}'.format(file_name), file_data.write)

            # Mengembalikan data file yang diunduh
            file_data.seek(0)
            return file_data.getvalue()  # Mengubah BytesIO menjadi bytes
    except Exception as e:
        # Tangani kesalahan jika terjadi
        print(f"Error during file download: {str(e)}")

# Fungsi untuk mendapatkan daftar file di server FTP
def get_file_list():
    try:
        with get_ftp_connection() as ftp:
            file_list = ftp.nlst()

        return file_list
    except Exception as e:
        # Tangani kesalahan jika terjadi
        print(f"Error during getting file list: {str(e)}")
        return []

# Fungsi untuk menjalankan aplikasi Flask dalam thread terpisah
def run_flask_app():
    app.run(debug=False)

# GUI Layout
layout = [
    [sg.Text("File Bridge - Unduh File", font=("Arial", 14))],
    [sg.Text("Nama File:", size=(10, 1)), sg.InputText(key="file_name"), sg.Button("Unduh", key="download")],
    [sg.Text("Daftar File di FTP:")],
    [sg.Listbox(values=[], size=(40, 10), key="file_list")],
    [sg.Text("", size=(40, 1), key="status_message")],
    [sg.Button("Unggah File", key="upload")],
    [sg.Button("Keluar")]
]

# Membuat window GUI
window = sg.Window("File Bridge", layout)

# Thread untuk menjalankan aplikasi Flask
flask_thread = threading.Thread(target=run_flask_app)

# Menjalankan thread Flask
flask_thread.start()

# Looping utama GUI
while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == "Keluar":
        break

    if event == "download":
        file_name = values["file_name"]
        if file_name == "":
            sg.popup("Mohon masukkan nama file yang ingin diunduh")
            continue

        file_data = download_file(file_name)
        if file_data:
            response = make_response(file_data)
            response.headers["Content-Disposition"] = f"attachment; filename={file_name}"
            window["status_message"].update("")
            sg.popup_scrolled("File berhasil diunduh", title="Status")
        else:
            window["status_message"].update("File tidak ditemukan")

    if event == "upload":
        file_path = sg.popup_get_file("Pilih file yang ingin diunggah", no_window=True)
        if file_path:
            with lock:
                file = open(file_path, "rb")
                upload_file(file)
                file.close()
            window["status_message"].update("File berhasil diunggah")
        else:
            window["status_message"].update("Pilih file yang ingin diunggah")

    with lock:
        file_list = get_file_list()
        window["file_list"].update(file_list)

# Menutup window GUI dan menghentikan aplikasi Flask
window.close()
flask_thread.join()