#!/usr/bin python
import importlib

import distribrewed.core.config as cfg
import distribrewed.core.defaults as defaults
import distribrewed.core.devices as devices
import distribrewed.core.utils.logging as log

import distribrewed.core.workers as workers


def construct_class_instance(class_module_path, param=None):
    class_data = class_module_path.split(".")
    module_path = ".".join(class_data[:-1])
    class_name = class_data[-1]
    module = importlib.import_module(module_path)
    class_handle = getattr(module, class_name)
    if param is None:
        return class_handle()
    return class_handle(param)


def load_device(config, owner, simulation):
    try:
        device_instance = construct_class_instance(config.device_class, config)
        if not issubclass(device_instance.__class__, devices.device.Device):
            log.error('Unable to load device from config: {0} is not a subclass of core.devices.device.Device'.
                  format(config.class_name))
            return None
        device_instance.owner = owner
        device_instance.simulation = simulation
        return device_instance
    except Exception as e:
        log.error('Unable to load device from config: {0}'.format(e.args[0]))
        return None


def load_worker(communication_config, config):
    try:
        worker_instance = construct_class_instance(config.class_name, config.name)
        if not issubclass(worker_instance.__class__, workers.baseworker.BaseWorker):
            log.error('Unable to load worker from config: {0} is not a subclass of core.workers.BaseWorker'.
                  format(config.class_name))
            return None
        ip = communication_config.ip
        master_port = int(communication_config.master_port)
        worker_port = int(communication_config.worker_port)
        worker_instance.init_communication(ip, master_port, worker_port)
        worker_instance.simulation = config.simulation
        worker_instance.input_config = config.inputs
        worker_instance.output_config = config.outputs
        return worker_instance
    except Exception as e:
        log.error('Unable to load worker from config: {0}'.format(e.args[0]))
        return None


def parse_config(configfile=defaults.DEFAULT_CONFIG):
    try:
        config = cfg.Config(configfile)
        return config
    except Exception as e:
        log.error('Unable to parse config: {0}'.format(e.args[0]))
        return None


def start_workers(config):
    workers = []
    for worker_config in config.workers:
        workers.append(load_worker(config.communication, worker_config))
    for worker in workers:
        worker.start()