#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Script for a distributed communication system using vector clocks
# for causal ordering of messages. Implements a process class that can send,
# receive, and handle messages in a distributed environment, ensuring that
# the causal relationship between events is maintained.

__Author__ = 'Kayuã Oleques'
__GitPage__ = 'https://github.com/kayua'
__version__ = '1.0.0'
__initial_data__ = '2024/10/20'
__last_update__ = '2024/10/22'
__credits__ = ['INF-UFRGS']

# Import necessary modules and handle missing dependencies
try:
    import sys
    import queue  # For managing message queues
    import logging  # For logging events and actions
    import threading  # For managing concurrent operations

    # Import custom modules for vector clocks and virtual sockets
    from Components.VectorClock import VectorClock
    from Components.VirtualSocket import VirtualSocket

except ImportError as error:
    # Handle missing imports and guide the user through environment setup
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
    sys.exit(-1)  # Exit if dependencies are not met


class ThreadProcess:
    """
    Manages sending and receiving messages using vector clocks to maintain
    causal ordering in a distributed environment. This class handles network
    communication and message queuing.
    """

    def __init__(self, process_id: int, total_processes: int, listen_port: int, send_port: int,
                 max_delay: float, address: str):
        """
        Initializes the process with unique parameters such as its ID, total
        number of processes, communication ports, and address.

        Args:
            process_id (int): ID of the current process.
            total_processes (int): Total number of processes in the distributed system.
            listen_port (int): The port where this process listens for incoming messages.
            send_port (int): The port used for sending messages.
            max_delay (float): Maximum allowable message transmission delay.
            address (str): The IP address of the current host.
        """

        self.process_id = process_id
        # Initializes vector clock and virtual socket for communication
        self.vector_clock = VectorClock(total_processes, process_id)
        self.virtual_socket = VirtualSocket(listen_port, send_port, max_delay, address)

        # Queues to manage messages: processed and pending
        self.message_queue = queue.Queue()
        self.pending_messages = queue.Queue()

        logging.info(f"Process {self.process_id} initialized with vector clock {self.vector_clock.vector}")

    def _build_message(self, message: str, sender_ip: str) -> str:
        """
        Prepares the message for sending, adding vector clock and sender's details.

        Args:
            message (str): The content to send.
            sender_ip (str): IP address of the sender.

        Returns:
            str: Formatted message containing the original content and metadata.
        """
        # Attach vector clock to the message
        vector_string = self.vector_clock.send_vector()
        return f"{message}:{self.process_id}:{sender_ip}:{vector_string}"

    def send_message(self, message: str, send_address: str) -> None:
        """
        Sends a message to a specified address and updates the vector clock.

        Args:
            message (str): Content of the message.
            send_address (str): The destination address of the message.
        """
        logging.info(f"Process {self.process_id}: Preparing to send message,"
                     f" current vector clock: {self.vector_clock.vector}")

        self.vector_clock.increment()  # Increment the vector clock before sending
        full_message = self._build_message(message, self.virtual_socket.get_local_ip())  # Construct the full message

        # Create a socket connection and send the message
        self.virtual_socket.create_send_message_socket(send_address)
        self.virtual_socket.send_message(full_message)
        logging.info(f"Process {self.process_id}: Message sent to {send_address},"
                     f" updated vector clock: {self.vector_clock.vector}")

    def receive_message(self, message: str) -> None:
        """
        Handles received messages by checking vector clock order, updating the clock,
        and processing the message or queuing it if out-of-order.

        Args:
            message (str): The message received, with vector clock info included.
        """
        logging.info(f"Process {self.process_id}: Received message: {message}")

        # Split the message into its components (content, sender info, and vector clock)
        message_split = message.split(':')
        content_message = message_split[0]
        sender_process_id = int(message_split[1])  # Extract sender's process ID
        sender_ip = message_split[2]  # Extract sender's IP address

        # Parse the vector clock from the message
        vector_clock_message = [int(x.strip()) for x in
                                message_split[3].replace('[',
                                                         '').replace(']', '').split(',')]

        # If the vector clock matches the expected clock, process the message
        if self.vector_clock.expected_clock(sender_process_id) == vector_clock_message:

            logging.info(f"Process {self.process_id}: Processing message from {sender_ip}, vector clock: {vector_clock_message}")
            self.vector_clock.update(vector_clock_message)  # Update vector clock after receiving
            logging.info(f"Process {self.process_id}: Vector clock updated to: {self.vector_clock.vector}")
            # Add the message to the queue for processing
            self.message_queue.put((content_message, sender_ip))
            self.process_pending_messages()  # Check and process any pending messages

        else:
            # If the clock is out-of-order, queue the message
            logging.warning(f"Process {self.process_id}: Out-of-order message from {sender_ip}, queuing.")
            self.pending_messages.put((message, sender_ip))

    def process_pending_messages(self):
        """
        Checks the queue of pending messages and processes them if their
        vector clocks are now in the correct order.
        """

        # Process all pending messages that can now be handled
        while not self.pending_messages.empty():

            pending_message, sender_ip = self.pending_messages.get()

            if self.can_process_pending_message(pending_message):

                logging.info(f"Process {self.process_id}: Processing queued message from {sender_ip}.")
                self.receive_message(pending_message)

    def can_process_pending_message(self, message: str) -> bool:
        """
        Checks if a pending message can be processed based on its vector clock.

        Args:
            message (str): The pending message to evaluate.

        Returns:
            bool: True if the message can be processed, False otherwise.
        """

        message_split = message.split(':')
        sender_process_id = int(message_split[1])
        vector_clock_message = [int(x.strip()) for x in
                                message_split[3].replace('[',
                                                         '').replace(']', '').split(',')]

        # Check if the message's vector clock matches the expected clock
        return self.vector_clock.expected_clock(sender_process_id) == vector_clock_message


def waiting_message(process):
    """
    Continuously polls for new messages and processes them when available.

    Args:
        process (ThreadProcess): The process instance to handle messages.
    """
    while True:

        if process.virtual_socket.received_messages_content:

            logging.info(f"Process {process.process_id}: New message received, processing.")
            # Process the received message
            process.receive_message(process.virtual_socket.received_messages_content)
            # Clear the message content to avoid reprocessing
            process.virtual_socket.received_messages_content = ""

        else:
            # Sleep briefly to avoid excessive CPU usage
            threading.Event().wait(0.1)