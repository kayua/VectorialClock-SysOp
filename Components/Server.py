#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
__Author__ = 'Kayuã Oleques'
__GitPage__ = 'unknown@unknown.com.br'
__version__ = '{1}.{0}.{0}'
__initial_data__ = '2024/10/20'
__last_update__ = '2024/10/22'
__credits__ = ['INF-UFRGS']


try:
    import sys
    import socket
    import logging

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

class Server:
    """
    Class responsible for running a UDP server that supports different message delivery semantics:
    'at most once', 'at least once', and 'exactly once'.
    """

    def __init__(self, server_address, semantic='at_most_once', timeout=None, max_messages=None):
        """
        Initializes the server with the provided address and message delivery semantic.

        Args:
            server_address (tuple): The address of the server as a (host, port) tuple.
            semantic (str): The message delivery semantic, one of 'at_most_once', 'at_least_once', or 'exactly_once'.
            timeout (float or None): The timeout for receiving messages in seconds. If None, no timeout is set.
            max_messages (int or None): The maximum number of messages to process. If None, the server runs indefinitely.
        """
        self.server_address = tuple(server_address)
        self.semantic = semantic
        self.timeout = timeout
        self.max_messages = max_messages
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.settimeout(timeout)
        self.processed_messages = set()
        self.message_count = 0

        self.logger = logging.getLogger(__name__)

        self.logger.info("Server Mode Initialized")

    def start(self):
        """
        Starts the server to listen for incoming UDP messages and process them
        according to the chosen semantic.
        """

        self.server_socket.bind(self.server_address)
        self.logger.info(f"Server started at {self.server_address}")

        while True:

            if self.max_messages and self.message_count >= self.max_messages:
                self.logger.info(f"Maximum message count reached ({self.max_messages}). Stopping server.")
                break

            try:

                # Wait to receive data from clients
                data, client_address = self.server_socket.recvfrom(1024)
                message = data.decode()

                self.logger.debug(f"Raw data received from {client_address}: {data}")
                self.logger.info(f"Received message from {client_address}: '{message}'")
                self.message_count += 1

                # Handle message based on the selected semantic
                if self.semantic == 'at_most_once':
                    self.handle_at_most_once(message)

                elif self.semantic == 'at_least_once':
                    self.handle_at_least_once(message, client_address)

                elif self.semantic == 'exactly_once':
                    self.handle_exactly_once(message, client_address)

            except socket.timeout:
                self.logger.warning("Socket timed out. Waiting for more messages.")

            except Exception as e:
                self.logger.error(f"An error occurred: {e}")

    def handle_at_most_once(self, message):
        """
        Handles messages using the 'at most once' semantic, where no acknowledgment
        is sent to the client and the message is processed without checking for duplicates.

        Args:
            message (str): The message received from the client.
        """
        self.logger.info(f"Handling message (at most once): '{message}'")

    def handle_at_least_once(self, message, client_address):
        """
        Handles messages using the 'at least once' semantic, where the server
        sends an acknowledgment (ACK) back to the client to confirm receipt.

        Args:
            message (str): The message received from the client.
            client_address (tuple): The address of the client sending the message.
        """
        self.logger.info(f"Handling message (at least once): '{message}' - Sending ACK to {client_address}")
        self.server_socket.sendto(b"ACK", client_address)

    def handle_exactly_once(self, message, client_address):
        """
        Handles messages using the 'exactly once' semantic, where duplicates are ignored
        and an acknowledgment (ACK) is only sent the first time the message is received.

        Args:
            message (str): The message received from the client.
            client_address (tuple): The address of the client sending the message.
        """

        if message not in self.processed_messages:
            self.logger.info(f"Handling message (exactly once): '{message}' - Sending ACK to {client_address}")
            self.processed_messages.add(message)
            self.server_socket.sendto(b"ACK", client_address)

        else:
            self.logger.warning(f"Duplicate message from {client_address} ignored: '{message}'")
