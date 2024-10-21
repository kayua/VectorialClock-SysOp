import socket
import threading
import time
import logging

from FidgeClock import FidgeClock
from VectorClock import VectorClock

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class Client:
    def __init__(self, process_id: int,
                 num_processes: int,
                 clock_type: str,
                 host: str = 'localhost',
                 port: int = 6100):
        """
        Initialize the client.

        :param process_id: Unique identifier for the process
        :param num_processes: Total number of processes in the system
        :param clock_type: Type of clock to use ('vector' or 'fidge')
        :param host: Hostname or IP address of the server
        :param port: Port number to connect to the server
        """
        self.process_id = process_id  # Set the unique process ID
        self.num_processes = num_processes  # Set the total number of processes
        self.clock_type = clock_type  # Set the type of clock

        # Initialize the appropriate clock based on the specified clock type
        if clock_type == 'vector':
            self.vector_clock = VectorClock(num_processes, process_id)
            logging.info(f"Initialized VectorClock for process {process_id}.")
        elif clock_type == 'fidge':
            self.vector_clock = FidgeClock()
            logging.info(f"Initialized FidgeClock for process {process_id}.")
        else:
            logging.error("Invalid clock type specified. Must be 'vector' or 'fidge'.")
            raise ValueError("Clock type must be 'vector' or 'fidge'.")

        # Create a socket for TCP communication
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Attempt to connect to the server
            self.socket.connect((host, port))
            logging.info(f"Process {process_id} connected to {host}:{port}.")
            # Send the process ID to the server
            self.socket.send(str(process_id).encode())
            logging.debug(f"Process ID {process_id} sent to server.")
        except Exception as e:
            logging.error(f"Connection failed: {e}")
            raise

    def send_message(self):
        """
        Send a message to the server containing the current clock value.
        This function increments the clock and constructs the message to be sent.
        """
        try:
            # Get the recipient process ID from user input
            recipient_id = int(input(f"Enter recipient process ID for process {self.process_id}: "))

            # Increment the clock based on its type and prepare the message
            if self.clock_type == 'vector':
                current_clock = self.vector_clock.send_vector()
                self.vector_clock.increment()  # Increment vector clock
                message = f"{recipient_id} - {self.vector_clock.send_vector()}"
                logging.debug(f"Process {self.process_id} incremented vector clock from {current_clock} to {self.vector_clock.send_vector()}.")
                logging.info(f"Current state of vector clock for process {self.process_id}: {self.vector_clock.send_vector()}")
            else:
                current_clock = self.vector_clock.get_value()
                self.vector_clock.increment()  # Increment Fidge clock
                message = f"{recipient_id} - {self.vector_clock.get_value()}"
                logging.debug(f"Process {self.process_id} incremented Fidge clock from {current_clock} to {self.vector_clock.get_value()}.")
                logging.info(f"Current state of Fidge clock for process {self.process_id}: {self.vector_clock.get_value()}")

            # Send the constructed message to the server
            self.socket.send(message.encode())
            logging.info(f"Process {self.process_id} sent message to {recipient_id} with clock: {message}")
        except Exception as e:
            logging.error(f"Failed to send message: {e}")

    def receive_message(self):
        """
        Continuously listen for messages from the server.
        When a message is received, update the clock accordingly.
        """
        while True:
            try:
                # Receive a message from the server
                message = self.socket.recv(1024).decode()
                if message:
                    # Split the received message into sender ID and clock value
                    sender_id, received_clock = message.split(' - ')
                    logging.info(f"Process {self.process_id} received message from {sender_id}: {received_clock}")

                    # Update the clock based on the clock type
                    if self.clock_type == 'vector':
                        logging.debug(f"Process {self.process_id} vector clock before update: {self.vector_clock.send_vector()}.")
                        received_vector = self.vector_clock.receive_vector(received_clock)
                        self.vector_clock.update(received_vector)
                        logging.debug(f"Process {self.process_id} updated vector clock to: {self.vector_clock.send_vector()}.")
                        logging.info(f"Current state of vector clock after receiving: {self.vector_clock.send_vector()}")
                    else:
                        logging.debug(f"Process {self.process_id} Fidge clock before update: {self.vector_clock.get_value()}.")
                        self.vector_clock.update()
                        logging.debug(f"Process {self.process_id} updated Fidge clock to: {self.vector_clock.get_value()}.")
                        logging.info(f"Current state of Fidge clock after receiving: {self.vector_clock.get_value()}")

            except Exception as e:
                logging.error(f"Error receiving message: {e}")
                break  # Exit loop on error

    def start(self):
        """
        Start the client to listen for incoming messages and periodically send messages.
        This method creates a thread for receiving messages and starts sending messages.
        """
        # Create a thread to handle incoming messages
        receive_thread = threading.Thread(target=self.receive_message)
        receive_thread.daemon = True  # Ensure the thread exits when the main program does
        receive_thread.start()
        logging.info(f"Process {self.process_id} started receiving messages.")

        # Simulate sending messages periodically
        while True:
            time.sleep(5)  # Simulate a delay between sending messages
            self.send_message()  # Send a message at regular intervals


if __name__ == "__main__":
    try:
        # Get user input for process configuration
        process_id = int(input("Enter process ID: "))  # Process ID
        num_processes = int(input("Enter total number of processes: "))  # Total number of processes
        clock_type = input("Choose clock type ('vector' or 'fidge'): ").strip().lower()  # Clock type choice

        # Create a Client instance and start it
        client = Client(process_id, num_processes, clock_type)
        client.start()  # Start the client's main functionality
    except Exception as e:
        logging.error(f"Error initializing client: {e}")