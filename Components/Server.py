import argparse
import queue
import threading

from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template

from ThreadProcess import ThreadProcess
from ThreadProcess import waiting_message

DEFAULT_PROCESS_ID = 0
DEFAULT_NUMBER_PROCESSES = 3
DEFAULT_LISTEN_PORT = 5050
DEFAULT_SEND_PORT = 5051
DEFAULT_MAX_DELAY = 1.0
DEFAULT_LOSS_PROBABILITY = 0.1
DEFAULT_ACK_LOSS_PROBABILITY = 0.05
DEFAULT_TIMEOUT = 2.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_IP_ADDRESS = '127.0.0.1'

app = Flask(__name__)
message_queue = queue.Queue()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/send_message', methods=['POST'])
def send_message():

    message, address = request.form['message'], request.form['address']
    communication_process.send_message(message, address)

    return jsonify({'status': 'Message sent'})


@app.route('/receive_message', methods=['GET'])
def receive_message():

    if not message_queue.empty():
        return jsonify({'message': str(message_queue.get())})

    else:
        return jsonify({'message': ''})


@app.route('/get_id', methods=['GET'])
def get_pid():
    with app.app_context():
        return jsonify({'pid': str(args.process_id)})



if __name__ == "__main__":

    # ArgumentParser configuration
    parser = argparse.ArgumentParser(description="Communication process configuration")

    parser.add_argument('--process_id', type=int,
                        default=DEFAULT_PROCESS_ID, help="Process ID")

    parser.add_argument('--number_processes', type=int,
                        default=DEFAULT_NUMBER_PROCESSES, help="Total number of processes")

    parser.add_argument('--listen_port', type=int,
                        default=DEFAULT_LISTEN_PORT, help="Listening port")

    parser.add_argument('--send_port', type=int,
                        default=DEFAULT_SEND_PORT, help="Sending port")

    parser.add_argument('--max_delay', type=float,
                        default=DEFAULT_MAX_DELAY, help="Maximum delay in seconds")

    parser.add_argument('--loss_probability', type=float,
                        default=DEFAULT_LOSS_PROBABILITY, help="Message loss probability")

    parser.add_argument('--ack_loss_probability', type=float,
                        default=DEFAULT_ACK_LOSS_PROBABILITY, help="ACK loss probability")

    parser.add_argument('--ack_timeout', type=float,
                        default=DEFAULT_TIMEOUT, help="ACK timeout in seconds")

    parser.add_argument('--max_retries', type=int,
                        default=DEFAULT_MAX_RETRIES, help="Maximum number of retries")

    parser.add_argument('--address', type=str,
                        default=DEFAULT_IP_ADDRESS, help="IP address")

    # Parsing the arguments
    args = parser.parse_args()

    # Initializing the communication process with the provided arguments
    communication_process = ThreadProcess(
        process_id=args.process_id,
        total_processes=args.number_processes,
        listen_port=args.listen_port,
        send_port=args.send_port,
        max_delay=args.max_delay,
        loss_probability=args.loss_probability,
        ack_loss_probability=args.ack_loss_probability,
        ack_timeout=args.ack_timeout,
        max_retries=args.max_retries,
        address=args.address
    )


    __thread__ = threading.Thread(target=waiting_message, args=(communication_process, message_queue), daemon=True)
    __thread__.start()

    app.run(debug=False, port=5002)
