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
        """
        Initializes a VirtualSocket that simulates unreliable TCP-like communication over UDP.

        Parameters:
        - listen_port: int : Port to listen for incoming messages.
        - send_port: int : Port to send messages.
        - max_delay: float : Maximum delay (in seconds) before sending a message.
        - loss_probability: float : Probability of a message being lost during transmission.
        - ack_loss_probability: float : Probability of an ACK message being lost.
        - ack_timeout: float : Time (in seconds) to wait for an ACK before retrying.
        - max_retries: int : Maximum number of retries before giving up on sending a message.
        """

        self.__send_address = None
        self.__send_socket = None
        logging.info(
            f"Initializing VirtualSocket with listen_port={listen_port}, send_port={send_port},"
            f" max_delay={max_delay}, loss_probability={loss_probability},"
            f" ack_loss_probability={ack_loss_probability},"
            f" ack_timeout={ack_timeout}, max_retries={max_retries}")

        # Save parameters
        self._listen_port = listen_port
        self._send_port = send_port
        self._max_delay = max_delay
        self._loss_probability = loss_probability
        self._ack_loss_probability = ack_loss_probability
        self._ack_timeout = ack_timeout
        self._max_retries = max_retries
        self.received_messages_content = ""
        self.received_messages_addr = ""

        # Initialize state variables
        self._is_listening = True  # Flag to control the listening loop
        self._acks_received = {}  # Track ACKs received for each message
        self.received_messages_id = set()  # Track message IDs to avoid duplicate processing

        # Create a UDP socket for listening and bind it to the specified port
        self.__listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__listen_socket.bind((address, listen_port))
        logging.debug("Listening socket created and bound to port.")

        # Start a separate thread to listen for incoming messages
        threading.Thread(target=self._listen, daemon=True).start()
        logging.info("Listener thread started.")

    def create_send_message_socket(self, send_address):

        # Create a UDP socket for sending messages
        self.__send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__send_address = (send_address, self._send_port)
        logging.debug(f"Sending socket created to send messages to {self.__send_address}.")

    def _listen(self):

        """ Listens for incoming UDP messages, processes them, and sends ACKs as needed. """
        logging.info(f"Listening for incoming messages on port {self._listen_port}")

        while self._is_listening:

            try:

                # Receive data from any source (buffer size: 1024 bytes)
                data, addr = self.__listen_socket.recvfrom(1024)
                message = data.decode()

                # Check if the message is an ACK
                if message.startswith("ACK:"):

                    message_id = message.split(":")[1]
                    self._acks_received[message_id] = True
                    logging.info(f"Received ACK from {addr} for message ID: {message_id}")

                else:

                    # Process regular messages (non-ACKs)
                    message_id, message_content = message.split(":", 1)

                    # If message ID is already processed, ignore duplicate
                    if message_id in self.received_messages_id:
                        logging.debug(f"Duplicate message '{message_content}' from {addr} ignored.")

                    else:

                        # Process the new message and send an ACK
                        logging.info(f"Received new message from {addr}: '{message_content}' with ID: {message_id}")
                        self.received_messages_id.add(message_id)
                        self.received_messages_content = message_content
                        self.received_messages_addr = addr
                        self._send_ack(addr, message_id)

            except Exception as e:
                logging.error(f"Error while listening: {e}")

    def send_message(self, message: str):

        """
        Sends a message with a random delay and handles potential message loss and retries.

        Parameters:
        - message: str : The content of the message to be sent.
        """
        message_id = str(random.randint(1000, 9999))  # Generate a unique ID for the message
        self._acks_received[message_id] = False  # Initialize ACK status for the message

        # Simulate a random delay before sending
        delay = random.uniform(0, self._max_delay)

        # Simulate message loss based on the specified probability
        if random.random() < self._loss_probability:
            logging.warning(f"Message lost: '{message}' with ID {message_id}. Loss probability triggered.")

        else:
            logging.info(f"Preparing to send message '{message}' with ID {message_id} after {delay:.2f}s delay.")
            # Send the message after the delay in a separate thread
            threading.Timer(delay, self._send, args=(message, message_id, 0)).start()

    def _send(self, message: str, msg_id: str, retries: int):
        """
        Sends the message and waits for an ACK. Retries if no ACK is received.

        Parameters:
        - message: str : The message content to be sent.
        - msg_id: str : Unique ID for the message.
        - retries: int : Number of retry attempts made so far.
        """
        if retries > self._max_retries:
            logging.error(f"Max retries reached for message '{message}' (ID {msg_id}). Abandoning send.")
            return

        try:
            # Send the message as a combination of ID and content
            full_message = f"{msg_id}:{message}"
            self.__send_socket.sendto(full_message.encode(), self.__send_address)
            logging.info(f"Message '{message}' (ID {msg_id}) sent. Waiting for ACK (Attempt {retries + 1}).")

            # Wait for the ACK with a timeout using a separate thread
            ack_thread = threading.Timer(self._ack_timeout, self._check_ack, args=(message, msg_id, retries))
            ack_thread.start()

        except Exception as e:
            logging.error(f"Error sending message '{message}' (ID {msg_id}): {e}")

    def _check_ack(self, message: str, msg_id: str, retries: int):
        """
        Checks if the ACK was received within the timeout period. Resends the message if not.

        Parameters:
        - message: str : The message content.
        - msg_id: str : Unique ID for the message.
        - retries: int : Current number of retry attempts.
        """
        if not self._acks_received[msg_id]:
            logging.warning(
                f"No ACK received for message '{message}' (ID {msg_id}). Retrying (Attempt {retries + 1})...")
            self._send(message, msg_id, retries + 1)

    def _send_ack(self, addr, msg_id: str):
        """
        Sends an ACK for a received message.

        Parameters:
        - addr : Address of the sender to send the ACK back to.
        - msg_id: str : Unique ID of the message being acknowledged.
        """
        # Simulate ACK loss based on probability
        if random.random() < self._ack_loss_probability:
            logging.warning(f"ACK lost for message {msg_id}. ACK loss probability triggered.")
        else:
            ack_message = f"ACK:{msg_id}"
            logging.info(f"Sending ACK to {addr} for message ID {msg_id}")
            self.__send_socket.sendto(ack_message.encode(), addr)

    def close(self):
        """ Closes the listening and sending sockets. """
        self._is_listening = False
        logging.info("Closing sockets and stopping listener.")
        self.__listen_socket.close()
        self.__send_socket.close()
        logging.debug("Sockets closed successfully.")
