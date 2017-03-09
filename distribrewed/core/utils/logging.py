#!/usr/bin python
import threading


LOG_RECEIVER_DB = 1
LOG_RECEIVER_STD = 2
LOG_RECEIVER_PROMETHEUS = 3
LOG_RECEIVER_BOTH = 4
LOG_RECEIVER = LOG_RECEIVER_PROMETHEUS

# Change to False to disable debugging messages
DEBUG_BREW = True
# Debug message types
DEBUG = 'd'
INFO = 'i'
WARNING = 'w'
ERROR = 'e'
LOG_TYPE_TEXT = {DEBUG: 'Debug', INFO: 'Info', WARNING: 'Warning', ERROR: 'Error'}


message_lock = threading.Lock()

def log_message(msg, msg_type, only_std=False):
    try:
        if only_std or LOG_RECEIVER == LOG_RECEIVER_BOTH or LOG_RECEIVER == LOG_RECEIVER_STD:
            print('[{0}] {1}'.format(msg_type, msg))
        elif LOG_RECEIVER == LOG_RECEIVER_PROMETHEUS:
            # TODO: Send to Prometheus
            print('[{0}] {1}'.format(msg_type, msg))

    except Exception as e:
        log_message('Unable to log {0} message: {1}'.format(LOG_TYPE_TEXT[msg_type], e.args[0]), ERROR)


def debug(message, only_std=False):
    if not DEBUG_BREW:
        return
    log_message(message, DEBUG, only_std)


def info(message, only_std=False):
    log_message(message, INFO, only_std)


def warning(message, only_std=False):
    log_message(message, WARNING, only_std)


def error(message, only_std=False):
    log_message(message, ERROR, only_std)
