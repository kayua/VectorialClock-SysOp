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
    import time
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

class Sender:
    def __init__(self, server_address, semantic):
        """
        Initialize the UDPSender instance.

        Args:
            server_address (tuple): The address of the server as a tuple (host, port).

        Raises:
            ValueError: If the server_address is not a valid tuple with two elements.
        """
        # Validate server address input
        if not isinstance(server_address, tuple) or len(server_address) != 2:
            logging.error("Invalid server address provided: %s", server_address)
            raise ValueError("Server address must be a tuple (host, port).")

        # Store the server address for sending messages
        self.server_address = server_address
        self.semantic = semantic
        # Create a UDP socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Create a logger for this module
        self.logger = logging.getLogger(__name__)

        # Log initialization of the Sender mode
        self.logger.info("Sender Mode Initialized")

    def send_message(self, message, semantic='at_most_once'):
        """
        Send a message to the server with specified semantic delivery.

        Args:
            message (str): The message to send.
            semantic (str): The delivery semantic ('at_most_once', 'at_least_once', 'exactly_once').

        Raises:
            ValueError: If an invalid semantic type is provided.
        """
        # Validate the semantic type
        if semantic not in ['at_most_once', 'at_least_once', 'exactly_once']:
            self.logger.error("Invalid semantic type provided: %s", semantic)
            raise ValueError("Semantic must be 'at_most_once', 'at_least_once', or 'exactly_once'.")

        self.logger.debug("Preparing to send message: '%s' with semantic '%s'", message, semantic)

        # Sending message with 'at_most_once' semantics
        if semantic == 'at_most_once':

            # Send message
            self.client_socket.sendto(message.encode(), self.server_address)

            # Log the send message
            self.logger.info("Sent message (at most once): '%s' to %s", message, self.server_address)

        # Sending message with 'at_least_once' semantics
        elif semantic == 'at_least_once':

            self.logger.info("Starting to send message with 'at_least_once' semantics.")

            while True:

                self.client_socket.sendto(message.encode(), self.server_address)  # Send message
                # Log the send message
                self.logger.info("Sent message (at least once): '%s' to %s", message, self.server_address)

                # Set a timeout for receiving acknowledgment
                self.client_socket.settimeout(1)

                try:
                    # Wait for acknowledgment from the server
                    data, _ = self.client_socket.recvfrom(1024)
                    # Log the received response
                    self.logger.debug("Received response: %s", data)

                    # Check if acknowledgment is received
                    if data == b"ACK":
                        self.logger.info("Acknowledgment received from server.")
                        break

                except socket.timeout:
                    # Log timeout and resend message
                    self.logger.warning("No ACK received, resending message: '%s'", message)

        # Sending message with 'exactly_once' semantics
        elif semantic == 'exactly_once':

            # Generate a unique identifier for the message
            message_id = int(time.time())
            self.logger.info("Starting to send message with 'exactly_once' semantics. Message ID: %d", message_id)

            while True:

                # Send message prefixed with message ID to ensure uniqueness
                self.client_socket.sendto(f"{message_id}:{message}".encode(), self.server_address)

                # Log the send message
                self.logger.info("Sent message (exactly once): '%s' with ID %d to %s",
                                 message, message_id, self.server_address)

                # Set a timeout for receiving acknowledgment
                self.client_socket.settimeout(1)

                try:
                    # Wait for acknowledgment from the server
                    data, _ = self.client_socket.recvfrom(1024)
                    # Log the received response
                    self.logger.debug("Received response: %s", data)

                    # Check if acknowledgment is received
                    if data == b"ACK":
                        self.logger.info("Acknowledgment received from server (exactly once).")
                        break

                except socket.timeout:
                    # Log timeout and resend message
                    self.logger.warning("No ACK received, resending message with ID %d: '%s'",
                                        message_id, message)

    def run(self):
        """
        Start the message sending loop.
        """

        while True:

            message = input("\nEnter the text to be sent (or 'exit' to leave):")

            if message.lower() == 'exit':
                self.logger.info("Exiting the message sending loop.\n")
                break

            self.send_message(message, self.semantic)

    def close(self):
        """
        Close the UDP socket and log the closure.

        Raises:
            RuntimeError: If an error occurs while closing the socket.
        """

        try:

            # Close the socket
            self.client_socket.close()

            # Log successful closure
            self.logger.info("Socket closed successfully.")

        except Exception as e:

            # Log any error during closure
            self.logger.error("Error occurred while closing the socket: %s", str(e))
            raise RuntimeError("Error occurred while closing the socket.") from e
