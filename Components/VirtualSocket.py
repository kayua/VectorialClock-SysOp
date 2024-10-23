#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
__Author__ = 'Kayuã Oleques'
__GitPage__ = 'https://github.com/kayua'
__version__ = '{1}.{0}.{0}'
__initial_data__ = '2024/10/20'
__last_update__ = '2024/10/23'
__credits__ = ['INF-UFRGS']

try:
    import sys
    import random
    import socket
    import logging
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
    """
    Simulates a virtual socket with message sending and receiving functionality.
    Introduces random delay in message sending for simulating network latency.
    """

    def __init__(self, listen_port: int, send_port: int, max_delay: float, address: str):
        """
        Initializes the VirtualSocket with listening and sending ports, and a maximum delay for sending messages.

        Args:
            listen_port (int): The port to listen on for incoming messages.
            send_port (int): The port to send messages to.
            max_delay (float): Maximum delay (in seconds) to introduce before sending messages.
            address (str): The local IP address to bind the listening socket.
        """
        self.__send_address = None  # Address to send messages to
        self.__send_socket = None  # Socket for sending messages
        self._listen_port = listen_port  # Port to listen for incoming messages
        self._send_port = send_port  # Port to send messages to
        self._max_delay = max_delay  # Maximum delay for simulating network latency
        self.received_messages_content = ""  # Content of the received messages
        self.received_messages_addr = ""  # Address from which the message was received
        self._is_listening = True  # Flag to keep the listening loop running
        self.__listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket for listening
        self.__listen_socket.bind((address, listen_port))  # Bind the socket to the local address and listening port

        logging.info(f"VirtualSocket initialized on {address}:{listen_port}")

        # Start a new thread to listen for incoming messages
        threading.Thread(target=self._listen, daemon=True).start()

    def create_send_message_socket(self, send_address: str):
        """
        Creates a socket to send messages to a specified address.

        Args:
            send_address (str): The IP address to send messages to.
        """
        self.__send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create UDP socket for sending
        self.__send_address = (send_address, self._send_port)  # Set the send address
        logging.info(f"Send socket created for sending to {send_address}:{self._send_port}")

    def _listen(self):
        """
        Listens for incoming messages on the listening socket.
        Updates the received message content and sender address when a message is received.
        """
        logging.info(f"Listening for incoming messages on port {self._listen_port}")

        while self._is_listening:

            try:

                # Receive up to 1024 bytes from the socket
                data, addr = self.__listen_socket.recvfrom(1024)
                message = data.decode()  # Decode the message to a string
                self.received_messages_content = message  # Update the received message content
                self.received_messages_addr = (addr[0], self._send_port)  # Save the sender's address
                logging.info(f"Received message from {addr}: {message}")

            except Exception as e:
                logging.error(f"Error while receiving message: {e}")

    def send_message(self, message: str):
        """
        Sends a message to the specified send address after a random delay.
        The delay is uniformly chosen between 0 and the maximum delay.

        Args:
            message (str): The message to be sent.
        """

        delay = random.uniform(0, self._max_delay)  # Generate a random delay
        logging.info(f"Sending message '{message}' after a delay of {delay:.2f} seconds")

        # Start a timer to send the message after the delay
        threading.Timer(delay, self._send, args=(message,)).start()

    def _send(self, message: str):
        """
        Sends the actual message through the socket to the previously defined address.

        Args:
            message (str): The message to be sent.
        """

        if self.__send_socket and self.__send_address:

            try:

                # Send the message to the destination address
                self.__send_socket.sendto(message.encode(), self.__send_address)
                logging.info(f"Message sent to {self.__send_address}: {message}")

            except Exception as e:
                logging.error(f"Error while sending message: {e}")

        else:
            logging.warning("Send socket or address is not defined. Message not sent.")

    def get_local_ip(self):
        """
        Returns the local IP address of the listening socket.

        Returns:
            str: Local IP address.
        """

        local_ip = self.__listen_socket.getsockname()[0]  # Retrieve the local IP address
        logging.info(f"Local IP address: {local_ip}")

        return local_ip