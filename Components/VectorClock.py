import logging

class VectorClock:
    """A class that implements a vector clock for distributed systems.

    Attributes:
        vector (list): A list representing the logical clock of the process.
        process_id (int): The unique identifier for this process.
    """

    def __init__(self, number_processes, process_id):
        """Initializes a new VectorClock instance.

        Args:
            number_processes (int): The total number of processes in the system.
            process_id (int): The unique identifier for this process.
        """
        self.vector = [0] * number_processes  # Initialize vector with zeros
        self.process_id = process_id
        logging.basicConfig(level=logging.INFO)
        logging.info(f"VectorClock initialized for process {self.process_id} with vector: {self.vector}")

    def increment(self):
        """Increments the logical clock for this process by one."""
        self.vector[self.process_id] += 1
        logging.info(f"Process {self.process_id} incremented its vector. New vector: {self.vector}")

    def update(self, received_vector):
        """Updates the vector clock based on a received vector from another process.

        Args:
            received_vector (list): A vector received from another process.
        """

        self.vector = [max(self.vector[i], received_vector[i]) for i in range(len(self.vector))]
        self.vector[self.process_id] += 1
        logging.info(f"Process {self.process_id} "
                     f"updated its vector with received vector {received_vector}. New vector: {self.vector}")

    def send_vector(self):
        """Sends the current vector as a comma-separated string.

        Returns:
            str: The vector in a string format.
        """
        vector_string = ','.join(map(str, self.vector))
        logging.info(f"Process {self.process_id} sending vector: {vector_string}")
        return vector_string

    def receive_vector(self, vector_string):
        """Receives a vector string and converts it into a list of integers.

        Args:
            vector_string (str): A comma-separated string representing a vector.

        Returns:
            list: The vector represented as a list of integers.
        """
        received_vector = list(map(int, vector_string.split(',')))
        logging.info(f"Process {self.process_id} received vector: {received_vector}")
        return received_vector
