import queue
import threading

from VectorClock import VectorClock
from VirtualSocket import VirtualSocket


class ThreadProcess:
    def __init__(self, process_id: int, total_processes: int, listen_port: int, send_port: int,
                 max_delay: float, address: str):
        self.process_id = process_id
        self.vector_clock = VectorClock(total_processes, process_id)
        self.virtual_socket = VirtualSocket(
            listen_port, send_port, max_delay,
            address
        )

        self.message_queue = queue.Queue()

    def _build_message(self, message: str) -> str:
        vector_string = self.vector_clock.send_vector()
        return f"{message}:{self.process_id}:{vector_string}"

    def send_message(self, message: str, send_address: str) -> None:

        print(f"Process {self.process_id}: Sending message, initial vector clock: {self.vector_clock.vector}")
        self.vector_clock.increment()  # Increment before sending the message
        full_message = self._build_message(message)
        self.virtual_socket.create_send_message_socket(send_address)
        self.virtual_socket.send_message(full_message)  # Pass the message ID explicitly
        print(f"Process {self.process_id}: Message sent, updated vector clock: {self.vector_clock.vector}")

    def receive_message(self, message: str) -> None:
        print(message)  # Verifique o que está sendo recebido
        message_split = message.split(':')
        vector_clock_message = [int(x.strip()) for x in message_split[2].replace('[', '').replace(']', '').split(',')]
        content_message = str(message_split[0])
        print(f"Process {self.process_id}: Received message with vector clock: {vector_clock_message}")
        self.vector_clock.update(vector_clock_message)
        print(f"Process {self.process_id}: Clock updated after receiving message: {self.vector_clock.vector}")
        self.message_queue.put(content_message)  # Adiciona à fila



def waiting_message(process):
    while True:

        if process.virtual_socket.received_messages_content:
            process.receive_message(process.virtual_socket.received_messages_content)
            process.virtual_socket.received_messages_content = ""

        else:
            threading.Event().wait(0.1)
