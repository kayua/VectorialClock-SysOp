#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
This script sets up a Flask web server that can send and receive messages
between communication processes, configured with various settings. The server
logs information, listens on a specified port, and manages messaging using
queues and threads.
"""

__Author__ = 'Kayuã Oleques'
__GitPage__ = 'https://github.com/kayua'
__version__ = '1.0.0'
__initial_data__ = '2024/10/20'
__last_update__ = '2024/10/22'
__credits__ = ['INF-UFRGS']

# Import necessary modules and handle missing dependencies
try:

    import os
    import sys
    import queue
    import logging
    import argparse
    import threading
    from View import View

    from flask import Flask
    from flask import jsonify
    from flask import request
    from flask import render_template

    from logging.handlers import RotatingFileHandler
    from ThreadProcess import ThreadProcess, waiting_message

except ImportError as error:
    # Handle missing imports and guide the user through environment setup
    print(error)
    print()
    print("1. (optional) Setup a virtual environment: ")
    print("  python3 - m venv ~/Python3env/ReliableCommunication ")
    print("  source ~/Python3env/DroidAugmentor/bin/activate ")
    print()
    print("2. Install requirements:")
    print("  pip3 install --upgrade pip")
    print("  pip3 install -r requirements.txt ")
    print()
    sys.exit(-1)  # Exit if dependencies are not met

# Disable Flask's default request logging
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# Default configuration values
DEFAULT_PATH_LOGS = 'Logs'
DEFAULT_PROCESS_ID = 0
DEFAULT_NUMBER_PROCESSES = 3
DEFAULT_LISTEN_PORT = 5050
DEFAULT_SEND_PORT = 5050
DEFAULT_MAX_DELAY = 10.0
DEFAULT_LOSS_PROBABILITY = 0.0
DEFAULT_ACK_LOSS_PROBABILITY = 0.00
DEFAULT_TIMEOUT = 2.0
DEFAULT_MAX_RETRIES = 100
DEFAULT_IP_ADDRESS = '127.0.0.1'

# Initialize Flask app and a message queue
app = Flask(__name__)
message_queue = queue.Queue()


@app.route('/')
def index():
    """
    Route to render the homepage. Serves index.html.
    """
    logging.info("Homepage accessed.")
    return render_template('index.html')


@app.route('/send_message', methods=['POST'])
def send_message():
    """
    API route to send a message. Expects 'message' and 'address' in the form data.
    The message is sent via the communication process.
    """
    message = request.form['message']
    address = request.form['address']
    logging.info(f"Received request to send message: '{message}' to {address}")
    communication_process.send_message(message, address)
    return jsonify({'status': 'Message sent'})


@app.route('/receive_message', methods=['GET'])
def receive_message():
    """
    API route to receive messages. Retrieves the next message from the queue
    if available and returns it, or returns a 'No new messages' status.
    """
    if not communication_process.message_queue.empty():
        message, sender_ip = communication_process.message_queue.get()
        logging.info(f"Message received from {sender_ip}: {message}")
        return jsonify({'message': message, 'sender_ip': sender_ip})

    logging.debug("No new messages.")
    return jsonify({'message': 'No new messages'}), 204


@app.route('/get_id', methods=['GET'])
def get_pid():
    """
    API route to get the process ID (pid).
    """
    logging.debug(f"Process ID requested: {args.process_id}")
    return jsonify({'pid': str(args.process_id)})


def show_all_settings(arguments):
    """
    Logs all settings and command-line arguments after parsing.
    Displays the command used to run the script along with the
    corresponding values for each argument.
    """
    # Log the command used to execute the script
    logging.info("Command:\n\t{0}\n".format(" ".join([x for x in sys.argv])))
    logging.info("Settings:")

    # Calculate the maximum length of argument names for formatting
    lengths = [len(x) for x in vars(arguments).keys()]
    max_length = max(lengths)

    # Log each argument and its value
    for keys, values in sorted(vars(arguments).items()):
        settings_parser = "\t" + keys.ljust(max_length, " ") + " : {}".format(values)
        logging.info(settings_parser)

    # Log a newline for spacing
    logging.info("")


def get_logs_path():
    """
    Returns the path to the logs directory.
    Creates the directory if it doesn't exist.
    """
    logs_dir = DEFAULT_PATH_LOGS
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir


def configure_logging(verbosity):
    """
    Configures logging to file and console with a rotating file handler.
    Adjusts log format based on verbosity level.
    """
    logger = logging.getLogger()

    # Default format for log messages
    logging_format = '%(asctime)s\t***\t%(message)s'
    if verbosity == logging.DEBUG:
        logging_format = '%(asctime)s\t***\t%(levelname)s {%(module)s} [%(funcName)s] %(message)s'

    from datetime import datetime
    LOGGING_FILE_NAME = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.log'
    logging_filename = os.path.join(get_logs_path(), LOGGING_FILE_NAME)

    logger.setLevel(verbosity)

    # Create rotating file handler
    rotatingFileHandler = RotatingFileHandler(filename=logging_filename, maxBytes=1000000, backupCount=5)
    rotatingFileHandler.setLevel(verbosity)
    rotatingFileHandler.setFormatter(logging.Formatter(logging_format))

    # Console handler
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(verbosity)
    consoleHandler.setFormatter(logging.Formatter(logging_format))

    # Clear previous handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Add new handlers
    logger.addHandler(rotatingFileHandler)
    logger.addHandler(consoleHandler)


if __name__ == "__main__":
    """
    Main entry point of the program. Parses command-line arguments, configures
    logging, starts the communication process, and runs the Flask web server.
    """
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Communication process configuration")
    parser.add_argument('--process_id', type=int, default=DEFAULT_PROCESS_ID, help="Process ID")
    parser.add_argument('--number_processes', type=int, default=DEFAULT_NUMBER_PROCESSES, help="Number of processes")
    parser.add_argument('--listen_port', type=int, default=DEFAULT_LISTEN_PORT, help="Listening port")
    parser.add_argument('--send_port', type=int, default=DEFAULT_SEND_PORT, help="Sending port")
    parser.add_argument('--max_delay', type=float, default=DEFAULT_MAX_DELAY, help="Maximum delay")
    parser.add_argument('--loss_probability', type=float, default=DEFAULT_LOSS_PROBABILITY, help="Loss probability")
    parser.add_argument('--ack_loss_probability', type=float, default=DEFAULT_ACK_LOSS_PROBABILITY,
                        help="ACK loss probability")
    parser.add_argument('--ack_timeout', type=float, default=DEFAULT_TIMEOUT, help="ACK timeout")
    parser.add_argument('--max_retries', type=int, default=DEFAULT_MAX_RETRIES, help="Maximum retries")
    parser.add_argument('--address', type=str, default=DEFAULT_IP_ADDRESS, help="Address")
    parser.add_argument('--flask_port', type=int, required=True, help="Flask port")
    args = parser.parse_args()

    # Configure logging with INFO verbosity
    configure_logging(logging.INFO)

    # Initialize the view and communication process
    view = View()
    view.print_view("")
    logging.info(f"Starting Flask server on http://127.0.0.1:{args.flask_port}")
    # Log the command-line settings
    show_all_settings(args)


    # Start the communication process thread
    communication_process = ThreadProcess(
        process_id=args.process_id,
        total_processes=args.number_processes,
        listen_port=args.listen_port,
        send_port=args.send_port,
        max_delay=args.max_delay,
        address=args.address
    )

    # Start a thread to handle waiting messages
    waiting_thread = threading.Thread(target=waiting_message, args=(communication_process,))
    waiting_thread.start()

    # Start the Flask app
    app.run(port=args.flask_port)
