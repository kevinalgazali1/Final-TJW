import tkinter as tk
from tkinter import filedialog
import socket
import os
import struct
import threading

TCP_IP = "192.168.6.230"  # Only a local server
TCP_PORT = 1456  # Just a random choice
BUFFER_SIZE = 1024  # Standard choice
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def connect_ftp():
    # Connect to the server
    print("Sending server request...")
    try:
        s.connect((TCP_IP, TCP_PORT))
        message_label.config(text="Connection successful")
    except:
        message_label.config(text="Connection unsuccessful. Make sure the server is online.")


import threading

def upload_file():
    # Upload a file
    file_path = filedialog.askopenfilename()
    if file_path:
        print("\nUploading file: {}...".format(file_path))
        try:
            # Check the file exists
            if not os.path.isfile(file_path):
                print("File does not exist. Make sure the file name was entered correctly.")
                message_label.config(text="File does not exist. Make sure the file name was entered correctly.")
                return

            # Disable upload button during file upload
            upload_button.config(state="disabled")

            # Create a new thread for file upload
            upload_thread = threading.Thread(target=upload_file_thread, args=(file_path,))
            upload_thread.start()

        except Exception as e:
            print("Error uploading file:", str(e))
            message_label.config(text="Error uploading file")

def upload_file_thread(file_path):
    try:
        # Make upload request
        s.send(b"UPLD")

        # Wait for server acknowledgement
        server_response = s.recv(BUFFER_SIZE)
        if server_response == b"OK":
            # Send file name size and file name
            s.send(struct.pack("h", len(file_path)))
            s.send(file_path.encode())

            # Wait for server response
            server_response = s.recv(BUFFER_SIZE)
            if server_response == b"OK":
                # Send file size
                file_size = os.path.getsize(file_path)
                s.send(struct.pack("i", file_size))

                # Send the file in chunks defined by BUFFER_SIZE
                # Doing it this way allows for unlimited potential file sizes to be sent
                with open(file_path, "rb") as file:
                    print("\nSending...")
                    sent_bytes = 0
                    while sent_bytes < file_size:
                        chunk = file.read(BUFFER_SIZE)
                        s.send(chunk)
                        sent_bytes += len(chunk)

                # Get upload performance details
                upload_time = struct.unpack("f", s.recv(4))[0]
                upload_size = struct.unpack("i", s.recv(4))[0]
                print("\nSent file: {}\nTime elapsed: {}s\nFile size: {}b".format(file_path, upload_time, upload_size))
                message_label.config(text="File uploaded successfully")
            else:
                print("Error sending file size")
                message_label.config(text="Error sending file size")
        else:
            print("Error sending file details")
            message_label.config(text="Error sending file details")

    except Exception as e:
        print("Error uploading file:", str(e))
        message_label.config(text="Error uploading file")

    # Enable upload button after file upload is finished
    upload_button.config(state="normal")



# Membuat window GUI
window = tk.Tk()
window.title("FTP Client")

# Membuat tombol "Connect" untuk menghubungkan ke FTP server
connect_button = tk.Button(window, text="Connect", command=connect_ftp)
connect_button.pack()

# Membuat tombol "Upload File" untuk mengunggah file ke server
upload_button = tk.Button(window, text="Upload File", command=upload_file)
upload_button.pack()

# Membuat label untuk menampilkan pesan
message_label = tk.Label(window, text="")
message_label.pack()

# Menjalankan GUI
window.mainloop()
