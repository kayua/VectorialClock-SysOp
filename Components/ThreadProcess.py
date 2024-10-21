import re

from VectorClock import VectorClock
from VirtualSocket import VirtualSocket


def regular_exp(message):

    return [int(x) for x in re.search(r'<strong>(.*?)</strong>', message).group(1).split(',')]

class ThreadProcess:
    def __init__(self, process_id: int,
                 total_processes: int,
                 listen_port: int,
                 send_port: int,
                 max_delay: float,
                 loss_probability: float,
                 ack_loss_probability: float,
                 ack_timeout: float,
                 max_retries: int,
                 address: str):
        """
        Initializes the process with a vector clock and a virtual socket.

        Args:
            process_id (int): The ID of the current process.
            total_processes (int): The total number of processes.
            listen_port (int): The port to listen for incoming messages.
            send_port (int): The port used for sending messages.
            max_delay (float): Maximum message delay in seconds.
            loss_probability (float): Probability of message loss.
            ack_loss_probability (float): Probability of ACK loss.
            ack_timeout (float): Timeout for waiting for an ACK in seconds.
            max_retries (int): Maximum number of retries for sending messages.
            address (str): Address of the process.
        """
        self.process_id = process_id
        self.vector_clock = VectorClock(total_processes, process_id)
        self.virtual_socket = VirtualSocket(
            listen_port, send_port, max_delay,
            loss_probability, ack_loss_probability,
            ack_timeout, max_retries, address
        )

    def _build_message(self, message: str) -> str:
        """
        Constructs the message by appending the vector clock state.

        Args:
            message (str): The content of the message to be sent.

        Returns:
            str: The complete message including the vector clock information.
        """
        vector_string = self.vector_clock.send_vector()
        return f"{message}<br>[<strong>{vector_string}</strong>]"

    def send_message(self, message: str, send_address: str) -> None:
        """
        Sends a message to the specified address, incrementing the vector clock.

        Args:
            message (str): The content of the message to be sent.
            send_address (str): The address to send the message to.
        """
        try:
            self.vector_clock.increment()
            full_message = self._build_message(message)
            self.virtual_socket.create_send_message_socket(send_address)
            self.virtual_socket.send_message(full_message)
        except Exception as e:
            print(f"Error sending message: {e}")

    def receive_message(self, message: str) -> None:
        """
        Processes the received message and updates the vector clock accordingly.

        Args:
            message (str): The received message content.
        """
        try:
            clean_message = regular_exp(message)  # Function to extract the cleaned content
            self.vector_clock.update(clean_message)
        except Exception as e:
            print(f"Error processing received message: {e}")

def waiting_message(process, message_queue):

    while True:

        content_message = process.virtual_socket.received_messages_content

        if content_message:
            process.receive_message(content_message)
            message_queue.put(" {} \n {}\n".format(
                process.virtual_socket.received_messages_addr, content_message))

        process.virtual_socket.received_messages_content = None