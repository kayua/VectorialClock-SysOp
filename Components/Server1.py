import logging
import queue
import re
import threading

from flask import Flask, render_template, request, jsonify

from VectorClock import VectorClock
from VirtualSocket import VirtualSocket

app = Flask(__name__)

# Queue to store messages
message_queue = queue.Queue()
DEFAULT_PID = 1


def extrair_vetor(texto):
    match = re.search(r'<strong>(.*?)</strong>', texto)

    vetor = match.group(1)
    return [int(x) for x in vetor.split(',')]
class Process:
    def __init__(self, process_id, total_processes, listen_port, send_port, max_delay, loss_probability,
                 ack_loss_probability, ack_timeout, max_retries, address):
        self.process_id = process_id
        self.vector_clock = VectorClock(total_processes, process_id)
        self.socket = VirtualSocket(listen_port, send_port, max_delay, loss_probability, ack_loss_probability,
                                    ack_timeout, max_retries, address)

    def send_message(self, message, send_address):
        self.vector_clock.increment()
        vector_string = self.vector_clock.send_vector()
        full_message = f"{message}<br>[<strong>{vector_string}</strong>]"
        self.socket.create_send_message_socket(send_address)
        self.socket.send_message(full_message)

    def receive_message(self, message):
        message = extrair_vetor(message)
        self.vector_clock.update(message)

def listen_for_messages(process):

    while True:

        message = process.socket.received_messages_content

        if message:
            process.receive_message(message)
            message_queue.put(" {} \n {}\n".format(process.socket.received_messages_addr, message))

        process.socket.received_messages_content = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    address = request.form['address']
    process2.send_message(message, address)
    return jsonify({'status': 'Message sent'})

@app.route('/receive_message', methods=['GET'])
def receive_message():
    if not message_queue.empty():
        message = message_queue.get()
        return jsonify({'message': str(message)})

    return jsonify({'message': ''})

@app.route('/get_id', methods=['GET'])
def get_pid():
    with app.app_context():
        return jsonify({'pid': str(DEFAULT_PID)})

if __name__ == "__main__":

    process2 = Process(
        process_id=DEFAULT_PID,
        total_processes=2,
        listen_port=5051,
        send_port=5050,
        max_delay=1.0,
        loss_probability=0.1,
        ack_loss_probability=0.05,
        ack_timeout=2.0,
        max_retries=3,
        address='127.0.0.1'
    )

    listener_thread = threading.Thread(target=listen_for_messages, args=(process2,), daemon=True)
    listener_thread.start()

    app.run(debug=False, port=5002)
