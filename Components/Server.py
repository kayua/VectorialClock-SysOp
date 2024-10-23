#!/usr/bin/python3
# -*- coding: utf-8 -*-

__Author__ = 'Kayuã Oleques'
__GitPage__ = 'https://github.com/kayua'
__version__ = '1.0.0'
__initial_data__ = '2024/10/20'
__last_update__ = '2024/10/22'
__credits__ = ['INF-UFRGS']

import argparse
import logging
import queue
import threading
from flask import Flask, jsonify, request, render_template
from ThreadProcess import ThreadProcess, waiting_message  # Supondo que essas classes estejam corretas

# Configurações de log
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# Configurações padrão
DEFAULT_PROCESS_ID = 0
DEFAULT_NUMBER_PROCESSES = 3
DEFAULT_LISTEN_PORT = 5050
DEFAULT_SEND_PORT = 5050
DEFAULT_MAX_DELAY = 1.0
DEFAULT_LOSS_PROBABILITY = 0.0
DEFAULT_ACK_LOSS_PROBABILITY = 0.00
DEFAULT_TIMEOUT = 2.0
DEFAULT_MAX_RETRIES = 100
DEFAULT_IP_ADDRESS = '127.0.0.1'

# Inicializando a aplicação Flask
app = Flask(__name__)
message_queue = queue.Queue()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    address = request.form['address']
    communication_process.send_message(message, address)
    return jsonify({'status': 'Message sent'})

@app.route('/receive_message', methods=['GET'])
def receive_message():
    if not communication_process.message_queue.empty():
        message, sender_ip = communication_process.message_queue.get()
        return jsonify({'message': message, 'sender_ip': sender_ip})  # Inclua o sender_ip
    return jsonify({'message': 'No new messages'}), 204

@app.route('/get_id', methods=['GET'])
def get_pid():
    return jsonify({'pid': str(args.process_id)})

if __name__ == "__main__":
    # Configuração do ArgumentParser
    parser = argparse.ArgumentParser(description="Communication process configuration")
    parser.add_argument('--process_id', type=int, default=DEFAULT_PROCESS_ID, help="Process ID")
    parser.add_argument('--number_processes', type=int, default=DEFAULT_NUMBER_PROCESSES, help="Number of processes")
    parser.add_argument('--listen_port', type=int, default=DEFAULT_LISTEN_PORT, help="Listening port")
    parser.add_argument('--send_port', type=int, default=DEFAULT_SEND_PORT, help="Sending port")
    parser.add_argument('--max_delay', type=float, default=DEFAULT_MAX_DELAY, help="Maximum delay")
    parser.add_argument('--loss_probability', type=float, default=DEFAULT_LOSS_PROBABILITY, help="Loss probability")
    parser.add_argument('--ack_loss_probability', type=float, default=DEFAULT_ACK_LOSS_PROBABILITY, help="ACK loss probability")
    parser.add_argument('--ack_timeout', type=float, default=DEFAULT_TIMEOUT, help="ACK timeout")
    parser.add_argument('--max_retries', type=int, default=DEFAULT_MAX_RETRIES, help="Maximum retries")
    parser.add_argument('--address', type=str, default=DEFAULT_IP_ADDRESS, help="Address")
    parser.add_argument('--flask_port', type=int, required=True, help="Flask port")
    args = parser.parse_args()

    print("Running on http://127.0.0.1:{}".format(args.flask_port))

    # Criando o processo de comunicação
    communication_process = ThreadProcess(
        process_id=args.process_id,
        total_processes=args.number_processes,
        listen_port=args.listen_port,
        send_port=args.send_port,
        max_delay=args.max_delay,
        address=args.address
    )

    # Iniciando a espera por mensagens
    waiting_thread = threading.Thread(target=waiting_message, args=(communication_process,))
    waiting_thread.start()

    # Iniciando a aplicação Flask
    app.run(port=args.flask_port)
