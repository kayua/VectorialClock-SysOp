import queue
import re

from VectorClock import VectorClock
from VirtualSocket import VirtualSocket


def regular_exp(message):
    match = re.search(r'\|(.*?)\|', message)
    if match:
        return [int(x.strip()) for x in match.group(1).split(',') if x.strip().isdigit()]
    return []



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
        self.expected_vector = [0] * total_processes
        self.message_queue = queue.Queue()

    def _build_message(self, message: str) -> str:
        vector_string = self.vector_clock.send_vector()
        return f"{message}|{vector_string}|"

    def send_message(self, message: str, send_address: str) -> None:

        try:
            self.vector_clock.increment()
            full_message = self._build_message(message)
            self.virtual_socket.create_send_message_socket(send_address)
            self.virtual_socket.send_message(full_message)

        except Exception as e:
            print(f"Error sending message: {e}")

    def receive_message(self, message: str) -> None:

        try:
            clean_message = regular_exp(message)
            current_vector = clean_message

            self.vector_clock.update(clean_message)

            if current_vector < self.expected_vector:
                self.message_queue.put(message)

            else:

                self.expected_vector = current_vector
                self.process_queued_messages()

        except Exception as e:
            print(f"Error processing received message: {e}")

    def process_queued_messages(self):

        while not self.message_queue.empty():

            queued_message = self.message_queue.get()
            queued_vector = regular_exp(queued_message)

            if queued_vector == self.expected_vector:
                self.expected_vector = queued_vector

            else:
                self.message_queue.put(queued_message)
                break


def waiting_message(process):

    while True:

        content_message = process.virtual_socket.received_messages_content

        if content_message:
            process.receive_message(content_message)

        process.virtual_socket.received_messages_content = None
