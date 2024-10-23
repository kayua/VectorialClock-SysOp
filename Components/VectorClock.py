class VectorClock:
    def __init__(self, total_processes: int, process_id: int):
        self.vector = [0] * total_processes
        self.process_id = process_id

    def increment(self):
        self.vector[self.process_id] += 1

    def send_vector(self):
        return ', '.join(map(str, self.vector))

    def update(self, received_vector):
        for i in range(len(self.vector)):
            self.vector[i] = max(self.vector[i], received_vector[i])
