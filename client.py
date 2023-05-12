import socket
import os
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
from tkinter import filedialog
from tkinter import *
from functools import partial
import time


######################## CHAT ###############################

HOST = '127.0.0.1'
PORT = 9090


class Client:

    def __init__(self, sock, chat_server, host, username):
        self = self
        self.sock = sock
        self.chat_server = chat_server

        gui = tkinter.Tk()
        gui.withdraw()

        self.nickname = username

        self.gui_done = False
        self.running = True

        self.peers = []

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)
        chat_manage_thread = threading.Thread(target=self.chat_manage)

        gui_thread.start()
        receive_thread.start()
        chat_manage_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.geometry('300x100')
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(
            self.win, text="List Friend", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.list_user = tkinter.Frame(self.win)
        self.list_user.pack(padx=20, pady=5)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def change_frame_users(self):
        for widget in self.list_user.winfo_children():
            print(widget)
            widget.destroy()
        while len(self.list_user.winfo_children()) != 0:
            {}
        for peer in self.peers:
            tkinter.Button(self.list_user, width=30, height=2,
                           text=peer[1], command=lambda: self.chat(peer[0])).pack()
        return True

    def chat(self, port):
        sock_chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_chat.connect((HOST, port))
        print('connect successfully')
        new_win = Chat(sock_chat, self.win, self.nickname)
        return True

    def chat_manage(self):
        while True:
            peer, address = self.chat_server.accept()
            print(f"Connected with {str(address)} !")

            new_win = Chat(peer, self.win, self.nickname)

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def receive(self):
        while self.running:
            try:
                self.peers = []
                message = self.sock.recv(1024).decode('utf-8')
                if message == "NICK":
                    info = self.nickname + '-' + str(self.chat_server_port)
                    self.sock.send(info.encode('utf-8'))
                else:
                    list_peer = message.split('/')[:-1]
                    for peer in list_peer:
                        [peer_port, peer_name] = peer.split('-')
                        peer_port = int(peer_port)
                        self.peers.append([peer_port, peer_name])
                    while self.gui_done == False:
                        {}
                    self.change_frame_users()

            except ConnectionAbortedError:
                break
            except:
                print('Error receiving messages')
                self.sock.close()
                break


class Chat:
    def __init__(self, peer, win, name1):
        self.peer = peer
        self.win = win
        self.name1 = name1

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.top = tkinter.Toplevel(self.win)
        self.top.geometry("750x700")
        self.top.title("Child Window")
        self.top.configure(bg="lightgray")

        self.top_label = tkinter.Label(self.top, text="Chat", bg="lightgray")
        self.top_label.config(font=("Arial", 12))
        self.top_label.pack(padx=20, pady=5)

        self.top_text_area = tkinter.scrolledtext.ScrolledText(self.top)
        self.top_text_area.pack(padx=20, pady=5)
        self.top_text_area.config(state="disabled")

        self.top_chat_label = tkinter.Label(
            self.top, text="Message: ", bg="lightgray")
        self.top_chat_label.config(font=("Arial", 12))
        self.top_chat_label.pack(padx=20, pady=5)

        self.top_input_area = tkinter.Text(self.top, height=3)
        self.top_input_area.pack(padx=20, pady=5)

        self.top_send_button = tkinter.Button(
            self.top, text="Send", command=self.write)
        self.top_send_button.config(font=("Arial", 12))
        self.top_send_button.pack(padx=20, pady=5)

        self.top_label_file_explorer = tkinter.Label(self.top,
                                                     text="File Explorer using Tkinter",
                                                     width=100, height=1,
                                                     fg="blue")
        self.top_label_file_explorer.config(font=("Arial", 12))
        self.top_label_file_explorer.pack(padx=20, pady=5)

        self.top_select_file_btn = tkinter.Button(
            self.top, text="Choose file", command=self.select_file)
        self.top_select_file_btn.config(font=("Arial", 12))
        self.top_select_file_btn.pack(padx=20, pady=5)

        self.gui_done = True

        self.top.protocol("WM_DELETE_WINDOW", self.stop)

    def select_file(self):
        filepath = filedialog.askopenfilename(
            title="Select a File",
            filetypes=(("Text files",
                        "*.txt*"),
                       ("all files",
                        "*.*")),
            parent=self.win)

        filename = os.path.basename(str(filepath))

        # Change label contents
        self.top_label_file_explorer.configure(text="File Opened: " + filename)
        file = open(filepath, 'r')
        data = file.read()
        print(data)

        self.peer.send("FILE".encode('utf-8'))

        self.peer.send(str(filename).encode('utf-8'))

        time.sleep(1)

        self.peer.send(data.encode('utf-8'))

    def write_text_area(self, message):
        self.top_text_area.config(state='normal')
        self.top_text_area.insert('end', message)
        self.top_text_area.yview('end')
        self.top_text_area.config(state='disabled')

    def write(self):
        message = f"{self.name1}: {self.top_input_area.get('1.0', 'end')}"
        self.write_text_area(message)
        self.peer.send(message.encode('utf-8'))
        self.top_input_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.top.destroy()
        self.peer.close()

    def receive(self):
        while self.running:
            try:
                print('before receive')
                message_chat = self.peer.recv(1024).decode('utf-8')
                print(message_chat)
                if message_chat == 'FILE':

                    filename = self.peer.recv(1024).decode('utf-8')
                    print(filename)
                    print('error getting file')

                    data = self.peer.recv(4048).decode('utf-8')
                    file = open("files/"+filename, 'w')
                    print('error opening files')
                    print(data)
                    file.write(data)
                    file.close()
                else:
                    print('after receive')
                    if self.gui_done:
                        self.write_text_area(message_chat)
            except ConnectionAbortedError:
                break
            except:
                print('Error receive_chat')
                self.peer.close()
                break

######################## LOGIN ###############################


def validateLogin(self, username, password):
    message = "LOGIN-" + username.get() + "-" + password.get() + \
        "-" + str(self.chat_server_port)
    self.sock.send(message.encode("utf-8"))
    return


def validateRegister(self, username, password):
    message = "REGISTER-" + username.get() + "-" + password.get() + \
        "-" + str(self.chat_server_port)
    self.sock.send(message.encode("utf-8"))
    return


class LOGIN:

    def __init__(self, host, port):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))

            self.chat_server = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.chat_server.bind((host, 0))
            self.chat_server.listen(4)

            self.chat_server_port = self.chat_server.getsockname()[1]

            receive_thread = threading.Thread(target=self.receive)
            receive_thread.start()

            # window
            self.win = Tk()
            self.win.geometry('200x100')
            self.win.title('Tkinter Login Form - pythonexamples.org')

            # username label and text entry box
            usernameLabel = Label(
                self.win, text="User Name").grid(row=0, column=0)
            username = StringVar()
            usernameEntry = Entry(
                self.win, textvariable=username).grid(row=0, column=1)

            # password label and password entry box
            passwordLabel = Label(
                self.win, text="Password").grid(row=1, column=0)
            password = StringVar()
            passwordEntry = Entry(self.win, textvariable=password,
                                  show='*').grid(row=1, column=1)

            global validateLogin
            validateLogin = partial(validateLogin, self, username, password)
            global validateRegister
            validateRegister = partial(
                validateRegister, self, username, password)

            # login button
            loginButton = Button(self.win, text="Login",
                                 command=validateLogin).grid(row=4, column=0)

            # register button
            registerButton = Button(self.win, text="Register",
                                    command=validateRegister).grid(row=4, column=1)

            self.win.protocol("WM_DELETE_WINDOW", self.stop)

            self.win.mainloop()
        except:
            print("Error connecting to server")

    def receive(self):
        while True:
            message = self.sock.recv(1024).decode("utf-8")

            [response, username] = message.split('-')
            if response == "SUCCESS":
                client = Client(self.sock, self.chat_server, HOST, username)
                self.stop()
                break

    def stop(self):
        self.win.destroy()
        exit(0)


login = LOGIN(HOST, PORT)
