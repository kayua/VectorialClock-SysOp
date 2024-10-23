import random
import socket
import threading


class VirtualSocket:
    def __init__(self, listen_port: int, send_port: int, max_delay: float, address: str):
        self.__send_address = None
        self.__send_socket = None
        self._listen_port = listen_port
        self._send_port = send_port
        self._max_delay = max_delay
        self.received_messages_content = ""
        self.received_messages_addr = ""
        self._is_listening = True
        self.__listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__listen_socket.bind((address, listen_port))
        threading.Thread(target=self._listen, daemon=True).start()

    def create_send_message_socket(self, send_address: str):
        """Create a socket for sending messages."""
        self.__send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__send_address = (send_address, self._send_port)

    def _listen(self):
        """Listen for incoming messages and process ACKs."""
        while self._is_listening:
            data, addr = self.__listen_socket.recvfrom(1024)
            message = data.decode()
            self.received_messages_content = message
            self.received_messages_addr = (addr[0], self._send_port)

    def send_message(self, message: str):
        delay = random.uniform(0, self._max_delay)
        threading.Timer(delay, self._send, args=(message,)).start()  # Fixed this line

    def _send(self, message: str):
        self.__send_socket.sendto(f"{message}".encode(), self.__send_address)