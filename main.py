#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
__Author__ = 'Kayuã Oleques'
__GitPage__ = 'unknown@unknown.com.br'
__version__ = '{1}.{0}.{0}'
__initial_data__ = '2024/10/20'
__last_update__ = '2024/10/22'
__credits__ = ['INF-UFRGS']


try:
    import os
    import sys
    import logging
    import argparse
    from datetime import datetime

    from Components.View import View
    from Components.Sender import Sender
    from Components.Server import Server
    from logging.handlers import RotatingFileHandler

except ImportError as error:

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
    sys.exit(-1)

DEFAULT_MODE = 'server'
DEFAULT_PORT_NUMBER = 8100
DEFAULT_IP_ADDRESS = 'localhost'
DEFAULT_SEMANTIC = 'at_most_once'
DEFAULT_LOG_LEVEL = 'INFO'
DEFAULT_PATH_LOGS = 'Logs'
DEFAULT_TIMEOUT = None
DEFAULT_MAX_MESSAGES = None


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
    # Defines the logs directory name as 'Logs'
    logs_dir = DEFAULT_PATH_LOGS

    # Creates the 'Logs' directory if it doesn't exist, the parameter exist_ok=True ensures
    os.makedirs(logs_dir, exist_ok=True)

    # Returns the path to the logs directory
    return logs_dir


def configure_logging(verbosity):
    logger = logging.getLogger()

    # Default format for log messages
    logging_format = '%(asctime)s\t***\t%(message)s'
    if verbosity == logging.DEBUG:
        logging_format = '%(asctime)s\t***\t%(levelname)s {%(module)s} [%(funcName)s] %(message)s'

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


def main():
    parser = argparse.ArgumentParser(description='Reliable Communication')

    parser.add_argument('--mode', default=DEFAULT_MODE, choices=['sender', 'server'],
                        help='Choose "sender" to send messages or "server" to receive messages.')

    parser.add_argument('--host', type=str, default=DEFAULT_IP_ADDRESS,
                        help='Host address for the server.')

    parser.add_argument('--port', type=int, default=DEFAULT_PORT_NUMBER,
                        help='Port number for the server.')

    parser.add_argument('--semantic', type=str, choices=['at_most_once', 'at_least_once', 'exactly_once'],
                        default=DEFAULT_SEMANTIC, help='Message handling semantic.')

    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        default=DEFAULT_LOG_LEVEL, help='Logging level for server operations.')

    parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT,
                        help='Socket timeout for receiving messages in seconds.')

    parser.add_argument('--max_messages', type=int, default=DEFAULT_MAX_MESSAGES,
                        help='Maximum number of messages to process before stopping.')

    args = parser.parse_args()

    # Set log level
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    configure_logging(log_level)


    if args.mode == 'sender':

        # Assume a View class exists for displaying information to the user
        view = View()
        # Display the initial view
        view.print_view("Sender Mode")
        # Log all settings
        show_all_settings(args)

        sender = Sender(server_address=(args.host, args.port), semantic=args.semantic)
        sender.run()
        sender.close()

    elif args.mode == 'server':

        # Display server mode message using pyfiglet
        view = View()
        view.print_view("Server Mode")

        # Log all settings
        show_all_settings(args)

        server = Server(server_address=(args.host, args.port), semantic=args.semantic,
                        timeout=args.timeout, max_messages=args.max_messages)
        server.start()


if __name__ == '__main__':
    main()


