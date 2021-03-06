import socket
import time
from threading import Thread
from Database import Database
from User import User


class BackgroundClientWorker(Thread):
    """Our background client worker for our client"""
    def __init__(self, client_socket: socket = None, database:Database = None, user: User = None, port: int = None):
        super().__init__()
        self.__client_socket = client_socket
        self.__server_socket = None
        self.__port = port
        self.__database = database
        self.__user = user
        self.__keep_clientRunning = True

    # Getters and Setters
    @property
    def client_socket(self):
        return self.__client_socket

    @client_socket.setter
    def client_socket(self, client_socket:socket):
        self.__client_socket = client_socket

    @property
    def database(self):
        return self.__database

    @database.setter
    def database(self, database:Database):
        self.__database = database

    @property
    def user(self):
        return self.__user

    @user.setter
    def user(self, user:User):
        self.__user = user

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, port:int):
        self.__port = port

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, client_id:int):
        self.__id = client_id

    @property
    def keep_running_client(self):
        return self.__keep_clientRunning

    @keep_running_client.setter
    def keep_running_client(self, state:bool):
        self.__keep_clientRunning = state

    # Methods
    def send_message(self, msg:str):
        self.display_message(f"""[SEND] {msg}""")
        self.__server_socket.send(msg.encode("UTF-8"))

    def receive_message(self, max_length:int = 1024):
        msg = self.__server_socket.recv(max_length).decode("UTF-8")
        print(f"""[RECV.BG] {msg}""")
        return msg

    def display_message(self, msg:str):
        print(f"""[BGCW] {msg}""")

    def check_for_messages(self):
        """Check if no list for messages exist"""
        if not list(self.__database.outgoing_messages.queue):
            pass
        elif list(self.__database.outgoing_messages.queue)[-1].receiver is self.__user:
            msg_info = self.__database.outgoing_messages.get()
            message = f"""R|{msg_info.sender.username}|{msg_info.id}|{msg_info.content}"""

            self.send_message(message)
            self.display_message(self.receive_message())
            self.display_message(self.__database.send_banner(msg_info.sender, msg_info.receiver,
                                                             msg_info.id))

        if not list(self.__database.outgoing_banners.queue):
            pass
        elif list(self.__database.outgoing_banners.queue)[-1].sender is self.__user:
            msg_info = self.__database.outgoing_banners.get()
            message = f"""OK|{msg_info.sender.username}|{msg_info.receiver.username}|{msg_info.content}"""
            self.send_message(message)
            self.display_message(self.receive_message())

    def run(self):
        """Our running program for background client worker, this will establish a socket and thread to listen
        to client requests such as viewing any messages or to disconnect/terminate"""

        self.display_message("SUCCESS: Connected to Client. Attempting connection to client background thread")

        while True:
            try:
                self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.__server_socket.connect((str(self.__client_socket.getpeername()[0]), self.__port))
                self.display_message("SUCCESS: Connected to client's server")
                break
            except socket.error as se:
                print("ERROR: Socket refused connection. Please try again.")
                time.sleep(2)

        while self.__keep_clientRunning:
            self.check_for_messages()
        self.__server_socket.close()

    def terminate_connection(self):
        """Sends request to close connection to server and disconnect bg client worker"""
        self.send_message("OUT|OK")
        self.__keep_clientRunning = False
