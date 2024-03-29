#!/usr/bin python
import yaml

import distribrewed.core.defaults as defaults
import distribrewed.core.utils.logging as log
from distribrewed.core.comm.connection import CONNECTION_MASTER_QUEUE

# Config file keys
CONFIG_COMMUNICATION = 'communication'
CONFIG_MASTER = 'master'
CONFIG_WORKERS = 'workers'
CONFIG_WORKER = 'worker'
CONFIG_NAME = 'name'
CONFIG_IP = 'ip'
CONFIG_MASTER_PORT = 'master_port'
CONFIG_WORKER_PORT = 'worker_port'
CONFIG_CLASS = 'class'
CONFIG_SIMULATION = 'simulation'
CONFIG_DEVICE_CLASS = 'device_class'
CONFIG_INPUTS = 'inputs'
CONFIG_INPUT = 'input'
CONFIG_OUTPUTS = 'outputs'
CONFIG_OUTPUT = 'output'
CONFIG_IO = 'io'
CONFIG_ACTIVE = 'active'
CONFIG_CALLBACK = 'callback'
CONFIG_CYCLE_TIME = 'cycle_time'


# Check if communication, master or workers sections
def is_communication(node):
    return str(node).startswith(CONFIG_COMMUNICATION)


def is_master(node):
    return str(node).startswith(CONFIG_MASTER)


def is_workers(node):
    return str(node).startswith(CONFIG_WORKERS)


def is_worker(node):
    return str(node).startswith(CONFIG_WORKER)


class IOConfig():
    def __init__(self, name, device_class, io, active, callback, cycle_time):
        self.name = name
        self.device_class = device_class
        self.io = io
        self.active = active.lower() == 'true'
        self.callback = callback
        self.cycle_time = float(cycle_time)

    def __str__(self):
        return '{0} of type {1} using io {2}'.format(self.name, self.device_class, self.io)


class CommunicationConfig():
    def __init__(self):
        self.ip = None
        self.master_port = None
        self.worker_port = None
        self.verify_data()

    def set(self, ip=defaults.MessageServerIP,
            master_port=defaults.MessageServerMasterPort,
            worker_port=defaults.MessageServerWorkerPort):
        self.ip = ip
        self.master_port = master_port
        self.worker_port = worker_port

    def verify_data(self):
        if self.ip is None or self.ip == '':
            self.ip = defaults.MessageServerIP
        if self.master_port is None or self.master_port == 0:
            self.master_port = defaults.MessageServerMasterPort
        if self.master_port is None or self.worker_port == 0:
            self.worker_port = defaults.MessageServerWorkerPort

    def set_from_yaml(self, yaml_data):
        self.ip = yaml_data[CONFIG_IP]
        self.master_port = int(yaml_data[CONFIG_MASTER_PORT])
        self.worker_port = int(yaml_data[CONFIG_WORKER_PORT])
        self.verify_data()

    def __str__(self):
        return 'Communication - {0}:{1}:{2}\r\n'.format(self.ip, self.master_port, self.worker_port)


class MasterConfig():
    def __init__(self):
        self.name = ''
        self.verify_data()

    def set(self, name):
        self.name = name

    def verify_data(self):
        if self.name is None:
            self.name = CONNECTION_MASTER_QUEUE

    def set_from_yaml(self, yamldata):
        self.name = yamldata[CONFIG_NAME]
        self.verify_data()

    def __str__(self):
        return 'Master({0}) - {1}:{2}\r\n'.format(self.name)


class WorkerConfig(MasterConfig):
    def __init__(self):
        MasterConfig.__init__(self)
        self.class_name = ''
        self.simulation = False
        self.outputs = []
        self.inputs = []

    def __str__(self):
        tmp = 'Worker ({0} as {3}) - {1}:{2}\r\n'.format(self.name, self.ip, self.master_port, self.class_name)
        for config in self.outputs.values():
            tmp = tmp + '* Output: {0}\r\n'.format(config)
        for config in self.inputs.values():
            tmp = tmp + '* Input: {0}\r\n'.format(config)
        return tmp

    def set_from_yaml(self, yaml_data):
        self.name = yaml_data[CONFIG_NAME]
        self.verify_data()
        self.class_name = yaml_data[CONFIG_CLASS]
        self.simulation = yaml_data[CONFIG_SIMULATION].lower() == 'true'
        if CONFIG_OUTPUTS in yaml_data and yaml_data[CONFIG_OUTPUTS] is not None:
            for iooutput in yaml_data[CONFIG_OUTPUTS]:
                iooutput = iooutput[CONFIG_OUTPUT]
                self.outputs.append(IOConfig(iooutput[CONFIG_NAME], iooutput[CONFIG_DEVICE_CLASS],
                                             iooutput[CONFIG_IO], iooutput[CONFIG_ACTIVE],
                                             iooutput[CONFIG_CALLBACK], iooutput[CONFIG_CYCLE_TIME]))
        if CONFIG_INPUTS in yaml_data and yaml_data[CONFIG_INPUTS] is not None:
            for ioinput in yaml_data[CONFIG_INPUTS]:
                ioinput = ioinput[CONFIG_INPUT]
                self.inputs.append(IOConfig(ioinput[CONFIG_NAME], ioinput[CONFIG_DEVICE_CLASS],
                                            ioinput[CONFIG_IO], ioinput[CONFIG_ACTIVE],
                                            ioinput[CONFIG_CALLBACK], ioinput[CONFIG_CYCLE_TIME]))


class Config():
    def __init__(self, configfile):
        self.communication = None
        self.master = None
        self.workers = []
        self.file = configfile
        self.read_config()

    def __str__(self):
        tmp = ''
        if self.master is not None:
            tmp += str(self.master)
            tmp += '\r\n'
        for worker in self.workers:
            tmp += str(worker)
            tmp += '\r\n'
        return tmp

    def read_config(self, configfile=''):
        try:
            if configfile != '':
                self.file = configfile
            raw = open(self.file, 'r')
            data = yaml.load(raw)
            self.communication = CommunicationConfig()
            communication_found = False
            master_found = False
            for name, section in data.items():
                if is_communication(name):
                    if communication_found:
                        log.warning('More than one communication node found, discarding')
                    else:
                        communication_found = True
                        self.communication.set_from_yaml(section)
                elif is_master(name):
                    if master_found:
                        log.warning('More than one master found, discarding')
                    else:
                        master_found = True
                        self.master = MasterConfig()
                        self.master.set_from_yaml(section)
                elif is_workers(name):
                    for worker_node in section:
                        worker = WorkerConfig()
                        worker.set_from_yaml(worker_node[CONFIG_WORKER])
                        self.workers.append(worker)
                else:
                    log.warning('Unknown module found {0}!'.format(str(name)))
            if not communication_found:
                log.warning('No communication node found, defaults will be used')
        except Exception as e:
            log.warning('Unable to load config file {0} : {1}'.format(self.file, e.args[0]))