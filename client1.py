import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, Scrollbar
from ftplib import FTP
from PIL import ImageTk, Image

# Konfigurasi FTP
ftp_host = '192.168.69.183'
ftp_port = 21

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('Aplikasi FTP Client')
        self.root.geometry('600x400')

        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 12, 'bold'))
        style.configure('TEntry', font=('Arial', 12))
        style.configure('TButton', font=('Arial', 12))

        # Menambahkan latar belakang gambar
        image = Image.open('bg.png')
        image = image.resize((600, 400), Image.ANTIALIAS)
        self.bg_image = ImageTk.PhotoImage(image)
        bg_label = ttk.Label(root, image=self.bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        label_username = ttk.Label(root, text='Username :')
        label_username.pack(pady=(100, 5))

        self.entry_username = ttk.Entry(root)
        self.entry_username.pack(pady=5)

        label_password = ttk.Label(root, text='Password :')
        label_password.pack(pady=5)

        self.entry_password = ttk.Entry(root, show='*')
        self.entry_password.pack(pady=5)

        toggle_button = ttk.Button(root, text='Toggle', command=self.toggle_password_input, style='TButton')
        toggle_button.pack(pady=5)

        login_button = ttk.Button(root, text='Login', command=self.login, style='TButton')
        login_button.pack(pady=(20, 50))

        # Untuk mengatur tampilan di tengah secara horizontal
        root.update()
        width = root.winfo_width()
        root.geometry(f"{width}x400+{root.winfo_screenwidth() // 2 - width // 2}+0")

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        ftp = FTP()
        try:
            ftp.connect(ftp_host, ftp_port)
            ftp.login(user=username, passwd=password)
            self.root.destroy()
            app_root = tk.Tk()
            FTPClientApp(app_root, ftp)
            app_root.mainloop()
        except:
            messagebox.showerror('Login Failed', 'Failed to connect to the FTP server.')

    def login_enter(self, event):
        self.login()

    def toggle_password_input(self):
        if self.entry_password.cget('show') == '':
            self.entry_password.configure(show='*')
        else:
            self.entry_password.configure(show='')

class FTPClientApp:
    def __init__(self, root, ftp):
        self.root = root
        self.selected_file = None
        self.root.title('Aplikasi FTP Client')
        self.root.geometry('600x400')

        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 12))
        style.configure('TButton', font=('Arial', 12))

        self.ftp = ftp

        image = Image.open('bg.png')
        image = image.resize((600, 400), Image.ANTIALIAS)
        self.bg_image = ImageTk.PhotoImage(image)
        bg_label = ttk.Label(root, image=self.bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        back_button = ttk.Button(root, text='Back', command=self.back_to_login, style='TButton')
        back_button.grid(row=0, column=0, padx=10, pady=10, sticky='nw')

        label = ttk.Label(root, text='Daftar File di Server FTP')
        label.grid(row=1, column=0, columnspan=3, pady=(10, 5))

        self.file_listbox = tk.Listbox(root)
        self.file_listbox.grid(row=2, column=0, columnspan=3, padx=10, pady=(0, 10))

        scrollbar = Scrollbar(root)
        scrollbar.grid(row=2, column=3, sticky='ns')
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_listbox.yview)

        upload_button = ttk.Button(root, text='Upload', command=self.upload_file, style='TButton')
        upload_button.grid(row=4, column=0, padx=10, pady=10, sticky='w')

        download_button = ttk.Button(root, text='Download', command=self.download_file, style='TButton')
        download_button.grid(row=3, column=1, padx=10, pady=(5, 50))

        delete_button = ttk.Button(root, text='Delete', command=self.delete_file, style='TButton')
        delete_button.grid(row=4, column=2, padx=10, pady=10, sticky='e')

        rename_button = ttk.Button(root, text='Rename', command=self.rename_file, style='TButton')
        rename_button.grid(row=3, column=0, padx=10, pady=(5, 50))

        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.columnconfigure(2, weight=1)
        root.rowconfigure(2, weight=1)

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

        current_dir = self.ftp.pwd()
        file_list = self.ftp.nlst()
        self.file_listbox.delete(0, 'end')
        for file_name in file_list:
            self.file_listbox.insert('end', file_name)
        
        # Scroll ke file terpilih setelah memperbarui daftar
        if self.selected_file:
            index = file_list.index(self.selected_file)
            self.file_listbox.see(index)

    def rename_file(self):
        selected_file = self.file_listbox.get(self.file_listbox.curselection())
        if selected_file:
            new_name = simpledialog.askstring('Rename File', 'Enter new file name:', initialvalue=selected_file)
            if new_name:
                try:
                    self.ftp.rename(selected_file, new_name)
                    self.refresh_file_list()
                except:
                    messagebox.showerror('Rename Failed', 'Failed to rename the file on the FTP server.')

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
