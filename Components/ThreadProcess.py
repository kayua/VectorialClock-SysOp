import queue
import threading

from VectorClock import VectorClock
from VirtualSocket import VirtualSocket


class ThreadProcess:
    def __init__(self, process_id: int, total_processes: int, listen_port: int, send_port: int,
                 max_delay: float, loss_probability: float, ack_loss_probability: float,
                 ack_timeout: float, max_retries: int, address: str):
        self.process_id = process_id
        self.vector_clock = VectorClock(total_processes, process_id)
        self.virtual_socket = VirtualSocket(
            listen_port, send_port, max_delay,
            loss_probability, ack_loss_probability,
            ack_timeout, max_retries, address
        )
        self.expected_vector = [0] * total_processes
        self.message_queue = queue.Queue()
        self.sent_messages = {}  # Store messages with their message_id

    def _build_message(self, message: str) -> str:
        vector_string = self.vector_clock.send_vector()
        return f"{message}:{self.process_id}:{vector_string}"

    def send_message(self, message: str, send_address: str) -> None:

        print(f"Process {self.process_id}: Sending message, initial vector clock: {self.vector_clock.vector}")
        self.vector_clock.increment()  # Increment before sending the message
        full_message = self._build_message(message)
        message_id = self.virtual_socket.create_send_message_socket(send_address)
        self.sent_messages[message_id] = full_message
        self.virtual_socket.send_message(full_message, message_id)  # Pass the message ID explicitly
        print(f"Process {self.process_id}: Message sent, updated vector clock: {self.vector_clock.vector}")
        print(f"Process {self.process_id}: Waiting for ACK from message {message_id}")
        self._check_ack(message_id, send_address)

    def _check_ack(self, message_id: str, send_address: str, retries = 2) -> None:
        """
        Verifies if an ACK has been received, retries if necessary.
        """
        if retries > self.virtual_socket._max_retries:
            print(f"Process {self.process_id}: Max retries reached for message {message_id}.")
            return

        if not self.virtual_socket._acks_received.get(message_id, False):
            # Retry sending the message if ACK not received

            original_message = self.sent_messages[message_id]  # Retrieve the original message
            self.virtual_socket._send(original_message, message_id, retries + 1)  # Use the same message ID
            threading.Timer(self.virtual_socket._ack_timeout, self._check_ack, args=(message_id, send_address, retries + 1)).start()
        else:

            print(f"Process {self.process_id}: ACK received for message {message_id}.")
            # Get the ACK and update the clock using the received vector from the ACK
            ack_vector = self.virtual_socket.received_ack_vector.get(message_id)
            print(message_id)
            print(self.virtual_socket.received_ack_vector.get(message_id))
            print("+++++++++++++++++++++++++++++++++++++++++++")
            if ack_vector:
                self.vector_clock.update(ack_vector)  # Update vector clock with the ACK vector
                print(f"Process {self.process_id}: Vector clock updated after receiving ACK: {self.vector_clock.vector}")

            print(self.sent_messages[message_id])

    def receive_message(self, message: str) -> None:
        print(message)
        message_split = message.split(':')
        vector_clock_message = [int(x.strip()) for x in message_split[2].replace('[', '').replace(']', '').split(',')]
        content_message = str(message_split[0])
        message_id = str(message_split[3])
        print(f"Process {self.process_id}: Received message with vector clock: {vector_clock_message}")
        self.vector_clock.update(vector_clock_message)
        print(f"Process {self.process_id}: Clock updated after receiving message: {self.vector_clock.vector}")

        # Increment before sending the ACK
        self.vector_clock.increment()
        print(f"Process {self.process_id}: Clock incremented to send ACK: {self.vector_clock.vector}")
        self.virtual_socket._send_ack(self.virtual_socket.received_messages_addr, message_id,
                                      str(self.vector_clock.vector), str(self.process_id))
        self.message_queue.put(content_message)



def waiting_message(process):
    while True:

        if process.virtual_socket.received_messages_content:
            process.receive_message(process.virtual_socket.received_messages_content)
            process.virtual_socket.received_messages_content = ""

        else:
            threading.Event().wait(0.1)
