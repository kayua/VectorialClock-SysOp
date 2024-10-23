import logging
import random
import socket
import threading

class VirtualSocket:
    def __init__(self, listen_port: int, send_port: int, max_delay: float, loss_probability: float,
                 ack_loss_probability: float, ack_timeout: float, max_retries: int, address: str):
        self.__send_address = None
        self.__send_socket = None

        self._listen_port = listen_port
        self._send_port = send_port
        self._max_delay = max_delay
        self._loss_probability = loss_probability
        self._ack_loss_probability = ack_loss_probability
        self._ack_timeout = 2.0
        self._max_retries = max_retries
        self.received_messages_content = ""
        self.received_messages_addr = ""
        self.received_ack_vector = {}  # Store vector clocks received with ACKs

        self._is_listening = True
        self._acks_received = {}
        self.received_messages_id = set()

        self.__listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__listen_socket.bind((address, listen_port))
        threading.Thread(target=self._listen, daemon=True).start()

    def create_send_message_socket(self, send_address: str):
        """Create a socket for sending messages."""
        self.__send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__send_address = (send_address, self._send_port)
        return str(random.randint(1000, 9999))  # Return a unique message ID

    def _listen(self):
        """Listen for incoming messages and process ACKs."""
        while self._is_listening:
            data, addr = self.__listen_socket.recvfrom(1024)
            message = data.decode()

            if message.startswith("ACK:"):
                print(f"Received message ACK: {message}")
                parts = message.split(":")
                print(parts)
                print('-------------------')
                message_id = str(parts[3])
                ack_vector = [int(x.strip()) for x in parts[2].replace('[', '').replace(']', '').split(',')]
                print(message_id)
                print("Message ID Received")
                self._acks_received[message_id] = True
                self.received_ack_vector[message_id] = ack_vector
                print(f"Received ACK for message ID {message_id}, vector clock: {ack_vector}")
            else:

                message_parts = message.split(":")
                message_id = str(message_parts[3])
                message_content = str(message_parts[0])

                if message_id in self.received_messages_id:
                    logging.debug(f"Duplicate message '{message_content}' from {addr} ignored.")
                else:
                    self.received_messages_id.add(message_id)
                    self.received_messages_content = message
                    self.received_messages_addr = (addr[0], self._send_port)



    def send_message(self, message: str, message_id: str):
        """Send a message with a unique ID."""
        self._acks_received[message_id] = False

        delay = random.uniform(0, self._max_delay)
        threading.Timer(delay, self._send, args=(message, message_id, 0)).start()

    def _send(self, message: str, msg_id: str, retries: int):
        """Send the message."""
        if retries > self._max_retries:
            print(f"Max retries reached for message ID {msg_id}.")
            return

        self.__send_socket.sendto(f"{message}:{msg_id}".encode(), self.__send_address)

    def _send_ack(self, send_address, message_id: str, vector_clock, process_id):
        """Send an ACK for a received message."""
        print("ENVIANDO ACK")
        self.create_send_message_socket(send_address)
        ack_message = f"ACK:{process_id}:{vector_clock}:{message_id}"
        self.__send_socket.sendto(ack_message.encode(), send_address)
