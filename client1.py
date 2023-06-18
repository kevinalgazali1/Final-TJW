import tkinter as tk
from tkinter import messagebox, filedialog
from ftplib import FTP
from PIL import Image, ImageTk
import tkinter.ttk as ttk

# Konfigurasi FTP
ftp_host = '192.168.1.14'
ftp_port = 21

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('Login')
        self.root.geometry('600x400')

        background_image = Image.open('bg.jpg')
        self.background_photo = ImageTk.PhotoImage(background_image)

        background_label = tk.Label(root, image=self.background_photo)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        label_username = tk.Label(root, text='Username')
        label_username.pack()

        self.entry_username = tk.Entry(root)
        self.entry_username.pack()

        label_password = tk.Label(root, text='Password')
        label_password.pack()

        self.entry_password = tk.Entry(root, show='*')
        self.entry_password.pack()

        login_button = tk.Button(root, text='Login', command=self.login, background='lightgreen')
        login_button.pack()

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        ftp = FTP()
        try:
            ftp.connect(ftp_host, ftp_port)
            ftp.login(user=username, passwd=password)
            self.root.destroy()
            app_root = tk.Tk()
            FTPClientApp(app_root, ftp, self.background_photo)
            app_root.mainloop()
        except:
            messagebox.showerror('Login Failed', 'Failed to connect to the FTP server.')

class FTPClientApp:
    def __init__(self, root, ftp, background_photo):
        self.root = root
        self.root.title('Aplikasi FTP')
        self.root.geometry('600x400')

        self.ftp = ftp
        self.background_photo = background_photo

        label = tk.Label(root, text='Daftar File di Server FTP')
        label.pack()

        self.file_listbox = tk.Listbox(root)
        self.file_listbox.pack()

        upload_button = tk.Button(root, text='Unggah File', command=self.upload_file)
        upload_button.pack()

        download_button = tk.Button(root, text='Unduh File', command=self.download_file)
        download_button.pack()

        delete_button = tk.Button(root, text='Hapus File', command=self.delete_file)
        delete_button.pack()

        back_button = tk.Button(root, text='Kembali ke Login', command=self.back_to_login)
        back_button.pack()

        self.refresh_file_list()

    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'rb') as file:
                file_name = file_path.split('/')[-1]  # Mengambil nama file dari path
                self.ftp.storbinary(f'STOR {file_name}', file)  # Menggunakan nama file
                self.refresh_file_list()

    def download_file(self):
        download_dir = filedialog.askdirectory()
        file_name = self.file_listbox.get(self.file_listbox.curselection())
        if file_name and download_dir:
            with open(f"{download_dir}/{file_name}", 'wb') as file:
                self.ftp.retrbinary(f'RETR {file_name}', file.write)

    def delete_file(self):
        file_name = self.file_listbox.get(self.file_listbox.curselection())
        if file_name:
            self.ftp.delete(file_name)
            self.refresh_file_list()

    def refresh_file_list(self):
        file_list = self.ftp.nlst()
        self.file_listbox.delete(0, 'end')
        for file_name in file_list:
            self.file_listbox.insert('end', file_name)

    def back_to_login(self):
        self.ftp.quit()
        self.root.destroy()
        root = tk.Tk()
        login_window = LoginWindow(root)
        root.mainloop()

def main():
    root = tk.Tk()
    login_window = LoginWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()
