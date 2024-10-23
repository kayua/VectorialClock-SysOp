#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
__Author__ = 'Kayuã Oleques'
__GitPage__ = 'https://github.com/kayua'
__version__ = '{1}.{0}.{0}'
__initial_data__ = '2024/10/20'
__last_update__ = '2024/10/22'
__credits__ = ['INF-UFRGS']

try:
    import sys
    import logging
    import random
    import socket
    import threading

except ImportError as error:

    print(error)
    print()
    print("1. (optional) Setup a virtual environment: ")
    print("  python3 - m venv ~/Python3env/ReliableCommunication ")
    print("  source ~/Python3env/DroidAugmentor/bin/activate ")
    print()
    print("2. Install requirements:")
    print("  pip3 install --upgrade pip")
    print("  pip3 install -r requirements.txt ")
    print()
    sys.exit(-1)

class VirtualSocket:
    def __init__(self,
                 listen_port: int,
                 send_port: int,
                 max_delay: float,
                 loss_probability: float,
                 ack_loss_probability: float,
                 ack_timeout: float,
                 max_retries: int,
                 address: str):


        self.__send_address = None
        self.__send_socket = None

        self._listen_port = listen_port
        self._send_port = send_port
        self._max_delay = max_delay
        self._loss_probability = loss_probability
        self._ack_loss_probability = ack_loss_probability
        self._ack_timeout = ack_timeout
        self._max_retries = max_retries
        self.received_messages_content = ""
        self.received_messages_addr = ""

        self._is_listening = True
        self._acks_received = {}
        self.received_messages_id = set()

        self.__listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__listen_socket.bind((address, listen_port))
        threading.Thread(target=self._listen, daemon=False).start()

    def create_send_message_socket(self, send_address):

        self.__send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__send_address = (send_address, self._send_port)

    def _listen(self):

        while True:

            data, addr = self.__listen_socket.recvfrom(1024)

            message = data.decode()

            if message.startswith("ACK:"):

                message_id = message.split(":")[1]
                self._acks_received[message_id] = True

            else:

                message_id, message_content = message.split(":", 1)

                if message_id in self.received_messages_id:
                    logging.debug(f"Duplicate message '{message_content}' from {addr} ignored.")

                else:

                    self.received_messages_id.add(message_id)
                    self.received_messages_content = message_content
                    self.received_messages_addr = (addr[0], self._send_port)
                    self._send_ack((addr[0], self._send_port), message_id)


    def send_message(self, message: str):

        message_id = str(random.randint(1000, 9999))
        self._acks_received[message_id] = False

        delay = random.uniform(0, self._max_delay)
        threading.Timer(delay, self._send, args=(message, message_id, 0)).start()

    def _send(self, message: str, msg_id: str, retries: int):

        if message.startswith("ACK:"):

            full_message = f"{msg_id}:{message}"
            self.__send_socket.sendto(full_message.encode(), self.__send_address)

        if retries > self._max_retries:
            logging.error(f"Max retries reached for message '{message}' (ID {msg_id}). Abandoning send.")
            return

        try:

            full_message = f"{msg_id}:{message}"
            self.__send_socket.sendto(full_message.encode(), self.__send_address)
            self.__send_socket.close()

        except Exception as e:
            logging.error(f"Error sending message '{message}' (ID {msg_id}): {e}")

    def _check_ack(self, message: str, msg_id: str, retries: int):

        if not self._acks_received[msg_id]:

            self._send(message, msg_id, retries + 1)

    def _send_ack(self, addr, msg_id: str):

        ack_message = f"ACK:{msg_id}"
        self.create_send_message_socket(addr[0])
        self.__send_socket.sendto(ack_message.encode(), addr)
        self.__send_socket.close()

    def close(self):

        self._is_listening = False
        self.__listen_socket.close()
        self.__send_socket.close()
