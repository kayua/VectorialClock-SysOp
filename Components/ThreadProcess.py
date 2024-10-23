import queue
import re
import threading
import logging
import random
import socket

from VectorClock import VectorClock
from VirtualSocket import VirtualSocket


def regular_exp(message):
    match = re.search(r'\|(.*?)\|', message)
    if match:
        return [int(x.strip()) for x in match.group(1).split(',') if x.strip().isdigit()]
    return []


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
        return f"{message}|{vector_string}|"

    def send_message(self, message: str, send_address: str) -> None:
        try:
            print(f"Process {self.process_id}: Sending message, initial vector clock: {self.vector_clock.vector}")
            self.vector_clock.increment()  # Increment before sending the message
            full_message = self._build_message(message)
            message_id = self.virtual_socket.create_send_message_socket(send_address)
            self.sent_messages[message_id] = full_message
            self.virtual_socket.send_message(full_message, message_id)  # Pass the message ID explicitly
            print(f"Process {self.process_id}: Message sent, updated vector clock: {self.vector_clock.vector}")
            self._check_ack(message_id, send_address)
        except Exception as e:
            print(f"Error sending message: {e}")

    def _check_ack(self, message_id: str, send_address: str, retries: int = 0) -> None:
        """
        Verifies if an ACK has been received, retries if necessary.
        """
        if retries > self.virtual_socket._max_retries:
            print(f"Process {self.process_id}: Max retries reached for message {message_id}.")
            return

        if not self.virtual_socket._acks_received.get(message_id, False):
            # Retry sending the message if ACK not received
            print(f"Process {self.process_id}: No ACK for message {message_id}, retrying...")
            original_message = self.sent_messages[message_id]  # Retrieve the original message
            self.virtual_socket._send(original_message, message_id, retries + 1)  # Use the same message ID
            threading.Timer(self.virtual_socket._ack_timeout, self._check_ack, args=(message_id, send_address, retries + 1)).start()
        else:
            print(f"Process {self.process_id}: ACK received for message {message_id}.")

    def receive_message(self, message: str) -> None:
        try:
            clean_message = regular_exp(message)
            print(f"Process {self.process_id}: Received message with vector clock: {clean_message}")
            self.vector_clock.update(clean_message)  # Update the clock with the received vector
            print(f"Process {self.process_id}: Clock updated after receiving message: {self.vector_clock.vector}")

            # Increment before sending the ACK
            self.vector_clock.increment()
            print(f"Process {self.process_id}: Clock incremented to send ACK: {self.vector_clock.vector}")
            self.virtual_socket._send_ack(self.virtual_socket.received_messages_addr, str(self.process_id))

            # Compare clean_message with expected_vector
            if clean_message < self.expected_vector:
                self.message_queue.put(message)
            else:
                self.expected_vector = clean_message
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
                self.message_queue.put(queued_message)  # Reinsert the message if it's not the expected one
                break


def waiting_message(process):
    while True:
        content_message = process.virtual_socket.received_messages_content
        if content_message:
            process.receive_message(content_message)
        process.virtual_socket.received_messages_content = None
