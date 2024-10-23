import logging
import random
import socket
import threading


class VirtualSocket:
    def __init__(self, listen_port: int, send_port: int, max_delay: float, loss_probability: float,
                 ack_loss_probability: float, ack_timeout: float, max_retries: int, address: str):
        self.__send_address = None
        self.__send_socket = None

        self._listen_port = listen_port
        self._send_port = send_port
        self._max_delay = max_delay
        self._loss_probability = loss_probability
        self._ack_loss_probability = ack_loss_probability
        self._ack_timeout = ack_timeout
        self._max_retries = max_retries
        self.received_messages_content = ""
        self.received_messages_addr = ""

        self._is_listening = True
        self._acks_received = {}
        self.received_messages_id = set()

        self.__listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__listen_socket.bind((address, listen_port))
        threading.Thread(target=self._listen, daemon=True).start()

    def create_send_message_socket(self, send_address: str):
        """Create a socket for sending messages."""
        self.__send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__send_address = (send_address, self._send_port)
        return str(random.randint(1000, 9999))  # Return a unique message ID

    def _listen(self):
        """Listen for incoming messages and process ACKs."""
        while self._is_listening:
            try:
                data, addr = self.__listen_socket.recvfrom(1024)
                message = data.decode()

                if message.startswith("ACK:"):
                    message_id = message.split(":")[1]
                    self._acks_received[message_id] = True
                    print(f"Received ACK for message ID {message_id}")

                else:
                    message_id, message_content = message.split(":", 1)
                    if message_id in self.received_messages_id:
                        logging.debug(f"Duplicate message '{message_content}' from {addr} ignored.")
                    else:
                        self.received_messages_id.add(message_id)
                        self.received_messages_content = message_content
                        self.received_messages_addr = (addr[0], self._send_port)
                        self._send_ack((addr[0], self._send_port), message_id)
            except Exception as e:
                logging.error(f"Error in listening: {e}")

    def send_message(self, message: str, message_id: str):
        """Send a message with a unique ID."""
        self._acks_received[message_id] = False

        delay = random.uniform(0, self._max_delay)
        threading.Timer(delay, self._send, args=(message, message_id, 0)).start()

    def _send(self, message: str, msg_id: str, retries: int):
        """Send a message, checking for ACK."""
        if retries > self._max_retries:
            logging.error(f"Max retries reached for message '{message}' (ID {msg_id}).")
            return

        try:
            full_message = f"{msg_id}:{message}"
            self.__send_socket.sendto(full_message.encode(), self.__send_address)
            print(f"Sent message ID {msg_id}")
        except Exception as e:
            logging.error(f"Error sending message '{message}' (ID {msg_id}): {e}")
            self._check_ack(message, msg_id, retries)

    def _check_ack(self, message: str, msg_id: str, retries: int):
        """Check for ACK receipt and resend if necessary."""
        if not self._acks_received.get(msg_id, False):
            delay = self._ack_timeout
            threading.Timer(delay, self._send, args=(message, msg_id, retries + 1)).start()

    def _send_ack(self, addr, msg_id: str):
        """Send an ACK to a sender."""
        ack_message = f"ACK:{msg_id}"
        self.create_send_message_socket(addr[0])
        print(f"Sending ACK for message ID {msg_id}")
        self.__send_socket.sendto(ack_message.encode(), addr)

    def close(self):
        """Close the sockets when done."""
        self.__send_socket.close()
        self.__listen_socket.close()