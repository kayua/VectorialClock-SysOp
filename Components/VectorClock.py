import logging

class VectorClock:
    """
    Implements a vector clock for tracking causality in distributed systems.
    Each process maintains a vector representing its own state and the perceived state of other processes.
    """

    def __init__(self, total_processes: int, process_id: int):
        """
        Initializes the vector clock for the process with the total number of processes
        and the unique ID for this process.

        Args:
            total_processes (int): Total number of processes in the distributed system.
            process_id (int): Unique ID of this process, used to index its entry in the vector clock.
        """
        self.vector = [0] * total_processes  # Initializes the vector clock with zeros
        self.process_id = process_id  # Stores the process ID
        logging.info(f"VectorClock initialized for process {self.process_id} with vector {self.vector}")

    def increment(self):
        """
        Increments the vector clock for the current process. This should be called before
        sending a message to reflect a local event.
        """
        self.vector[self.process_id] += 1  # Increment the current process's clock
        logging.info(f"Process {self.process_id}: Vector clock incremented to {self.vector}")

    def send_vector(self) -> str:
        """
        Converts the vector clock to a string format, to be included in outgoing messages.

        Returns:
            str: The vector clock as a comma-separated string.
        """
        vector_str = ', '.join(map(str, self.vector))  # Convert vector to a string
        logging.info(f"Process {self.process_id}: Sending vector clock {self.vector}")
        return vector_str

    def update(self, received_vector: list):
        """
        Updates the local vector clock based on a received vector from another process.
        The local clock is updated to the maximum value for each entry between the local
        clock and the received clock.

        Args:
            received_vector (list): The vector clock received from another process.
        """
        logging.info(f"Process {self.process_id}: Received vector clock {received_vector} for update")
        # Update the local vector to the max of the current and received vector values
        for i in range(len(self.vector)):
            old_value = self.vector[i]
            self.vector[i] = max(self.vector[i], received_vector[i])
            logging.debug(f"Process {self.process_id}: Updated vector clock index {i} from {old_value} to {self.vector[i]}")
        logging.info(f"Process {self.process_id}: Vector clock updated to {self.vector}")

    def expected_clock(self, sender_process_id: int) -> list:
        """
        Computes the expected vector clock for a given sending process.
        The expected clock is the local clock with the sender's entry incremented by 1.

        Args:
            sender_process_id (int): The process ID of the sender.

        Returns:
            list: The expected vector clock where the sender's clock has been incremented by 1.
        """
        expected = self.vector.copy()  # Create a copy of the current vector clock
        expected[sender_process_id] += 1  # Increment the sender's clock
        logging.info(f"Process {self.process_id}: Expected vector clock for sender {sender_process_id} is {expected}")
        return expected
