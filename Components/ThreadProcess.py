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
        self.pending_messages = queue.Queue()  # Fila para mensagens pendentes

    def _build_message(self, message: str, sender_ip: str) -> str:
        vector_string = self.vector_clock.send_vector()
        return f"{message}:{self.process_id}:{sender_ip}:{vector_string}"

    def send_message(self, message: str, send_address: str) -> None:
        print(f"Process {self.process_id}: Sending message, initial vector clock: {self.vector_clock.vector}")
        self.vector_clock.increment()  # Increment before sending the message
        full_message = self._build_message(message, self.virtual_socket.get_local_ip())  # Pass local IP
        self.virtual_socket.create_send_message_socket(send_address)
        self.virtual_socket.send_message(full_message)
        print(f"Process {self.process_id}: Message sent, updated vector clock: {self.vector_clock.vector}")

    def receive_message(self, message: str) -> None:
        print(message)  # Check what is being received
        message_split = message.split(':')
        content_message = str(message_split[0])
        sender_process_id = int(message_split[1])  # Converter para inteiro
        sender_ip = message_split[2]
        vector_clock_message = [int(x.strip()) for x in message_split[3].replace('[', '').replace(']', '').split(',')]

        # Verifica se o vetor de relógio recebido é o esperado
        if self.vector_clock.expected_clock(sender_process_id) == vector_clock_message:
            print(f"Process {self.process_id}: Received message from {sender_ip} (Process ID: {sender_process_id}) with vector clock: {vector_clock_message}")
            self.vector_clock.update(vector_clock_message)
            print(f"Process {self.process_id}: Clock updated after receiving message: {self.vector_clock.vector}")
            self.message_queue.put((content_message, sender_ip))  # Adicione o sender_ip à fila
            self.process_pending_messages()  # Processar mensagens pendentes
        else:
            print(f"Process {self.process_id}: Unexpected vector clock received, queuing message.")
            self.pending_messages.put((message, sender_ip))  # Adiciona mensagem à fila de pendentes

    def process_pending_messages(self):
        while not self.pending_messages.empty():
            pending_message, sender_ip = self.pending_messages.get()
            if self.can_process_pending_message(pending_message):  # Checa se a mensagem pode ser processada
                print(f"Process {self.process_id}: Processing pending message from {sender_ip}.")
                self.receive_message(pending_message)

    def can_process_pending_message(self, message: str) -> bool:
        # Implementar lógica para verificar se a mensagem pode ser processada
        message_split = message.split(':')
        sender_process_id = int(message_split[1])
        vector_clock_message = [int(x.strip()) for x in message_split[3].replace('[', '').replace(']', '').split(',')]
        return self.vector_clock.expected_clock(sender_process_id) == vector_clock_message


def waiting_message(process):
    while True:
        if process.virtual_socket.received_messages_content:
            process.receive_message(process.virtual_socket.received_messages_content)
            process.virtual_socket.received_messages_content = ""
        else:
            threading.Event().wait(0.1)