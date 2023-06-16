# import tkinter as tk
# from tkinter import filedialog
# from ftplib import FTP

# class FTPClientGUI:
#     def _init_(self, root):
#         self.root = root
#         self.root.title("FTP Client")
        
#         # Membuat antarmuka pengguna
#         self.create_widgets()
        
#         # Membuat objek FTP
#         self.ftp = FTP()
    
#     def create_widgets(self):
#         # Label untuk server
#         server_label = tk.Label(self.root, text="Server:")
#         server_label.pack()

#         # Entry untuk input server
#         self.server_entry = tk.Entry(self.root)
#         self.server_entry.pack()

#         # Label untuk username
#         username_label = tk.Label(self.root, text="Username:")
#         username_label.pack()

#         # Entry untuk input username
#         self.username_entry = tk.Entry(self.root)
#         self.username_entry.pack()

#         # Label untuk password
#         password_label = tk.Label(self.root, text="Password:")
#         password_label.pack()

#         # Entry untuk input password
#         self.password_entry = tk.Entry(self.root, show="*")
#         self.password_entry.pack()

#         # Tombol untuk menghubungkan ke server
#         connect_button = tk.Button(self.root, text="Connect", command=self.connect_to_server)
#         connect_button.pack()

#         # Tombol untuk mengunggah file
#         upload_button = tk.Button(self.root, text="Upload", command=self.upload_file)
#         upload_button.pack()

#         # Tombol untuk mengunduh file
#         download_button = tk.Button(self.root, text="Download", command=self.download_file)
#         download_button.pack()

#     def connect_to_server(self):
#         # Mengambil informasi server, username, dan password dari input pengguna
#         server = self.server_entry.get()
#         username = self.username_entry.get()
#         password = self.password_entry.get()

#         # Menghubungkan ke server FTP
#         try:
#             self.ftp.connect(server)
#             self.ftp.login(username, password)
#             print("Connected to FTP server")
#         except Exception as e:
#             print("Error connecting to FTP server:", str(e))

#     def upload_file(self):
#         # Memilih file yang akan diunggah menggunakan dialog
#         file_path = filedialog.askopenfilename()

#         # Memeriksa apakah file dipilih
#         if file_path:
#             try:
#                 # Mengunggah file ke server FTP
#                 file_name = file_path.split("/")[-1]
#                 with open(file_path, "rb") as file:
#                     self.ftp.storbinary("STOR " + file_name, file)
#                 print("File uploaded successfully")
#             except Exception as e:
#                 print("Error uploading file:", str(e))

#     def download_file(self):
#         # Memilih file yang akan diunduh menggunakan dialog
#         file_path = filedialog.asksaveasfilename()

#         # Memeriksa apakah file disimpan dengan nama yang valid
#         if file_path:
#             try:
#                 # Mengunduh file dari server FTP
#                 file_name = file_path.split("/")[-1]
#                 with open(file_path, "wb") as file:
#                     self.ftp.retrbinary("RETR " + file_name, file.write)
#                 print("File downloaded successfully")
#             except Exception as e:
#                 print("Error downloading file:", str(e))

# # if _name_ == "_main_":
#     # Membuat instance dari Tkinter
#     root = tk.Tk()
    
#     # Membuat objek FTPClientGUI
#     ftp_client_gui = FTPClientGUI(root)
    
#     # Menjalankan aplikasi GUI
#     root.mainloop()

from ftplib import FTP

# Konfigurasi server FTP
FTP_HOST = "192.168.1.13"  # Alamat server FTP
FTP_PORT = 21  # Port server FTP
FTP_USER = "vin"  # Nama pengguna FTP
FTP_PASS = "1234"  # Kata sandi pengguna FTP

def upload_file(file_name):
    # Upload file ke server FTP
    try:
        ftp = FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.storbinary("STOR " + file_name, open(file_name, "rb"))
        ftp.quit()
        print("File uploaded successfully.")
    except Exception as e:
        print("Error uploading file:", str(e))

def list_files():
    # Mendapatkan daftar file yang tersedia di server FTP
    try:
        ftp = FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        file_list = ftp.nlst()
        for file_name in file_list:
            print(file_name)
        ftp.quit()
    except Exception as e:
        print("Error retrieving file list:", str(e))

def download_file(file_name):
    # Download file dari server FTP
    try:
        ftp = FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.retrbinary("RETR " + file_name, open(file_name, "wb").write)
        ftp.quit()
        print("File downloaded successfully.")
    except Exception as e:
        print("Error downloading file:", str(e))

def delete_file(file_name):
    # Menghapus file dari server FTP
    try:
        ftp = FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.delete(file_name)
        ftp.quit()
        print("File deleted successfully.")
    except Exception as e:
        print("Error deleting file:", str(e))

# Menjalankan FTP client
print("\nWelcome to the FTP client.")
print("Available commands:")
print("UPLOAD file_path  : Upload file to FTP server")
print("LIST              : List files on FTP server")
print("DOWNLOAD file     : Download file from FTP server")
print("DELETE file       : Delete file from FTP server")
print("QUIT              : Exit FTP client")

while True:
    command = input("\nEnter a command: ").split()
    if not command:
        continue

    if command[0].upper() == "UPLOAD":
        if len(command) > 1:
            upload_file(command[1])
        else:
            print("Please provide a file path.")
    elif command[0].upper() == "LIST":
        list_files()
    elif command[0].upper() == "DOWNLOAD":
        if len(command) > 1:
            download_file(command[1])
        else:
            print("Please provide a file name.")
    elif command[0].upper() == "DELETE":
        if len(command) > 1:
            delete_file(command[1])
        else:
            print("Please provide a file name.")
    elif command[0].upper() == "QUIT":
        break
    else:
        print("Command not recognized; please try again.")
