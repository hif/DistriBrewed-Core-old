#!/usr/bin python
# The default config file name
import os

DEFAULT_CONFIG = os.getenv('CONFIG_FILE', 'config/demo_mash_config.yml')

MessageServerIP = None
MessageServerMasterPort = None
MessageServerWorkerPort = None


# Doing this for easier unit tests
def load_from_env():
    global MessageServerIP;  MessageServerIP = os.getenv('MASTER_IP', '0.0.0.0')
    global MessageServerMasterPort; MessageServerMasterPort = int(os.getenv('MASTER_PORT', '9991'))
    global MessageServerWorkerPort; MessageServerWorkerPort = int(os.getenv('WORKER_PORT', '9992'))

load_from_env()

# TODO: REMOVE DB stuff from core
DefaultDBHost = 'localhost'
DefaultDBPort = '5432'
DefaultDBUser = 'twistedbrewer'
DefaultDBPassword = 'twistedbrewer'
DefaultDB = 'twistedbrew'

DefaultDBConnectionString = "dbname='{4}' user='{2}' host='{0}' port='{1}' password='{3}'".\
    format(DefaultDBHost, DefaultDBPort, DefaultDBUser, DefaultDBPassword, DefaultDB)
