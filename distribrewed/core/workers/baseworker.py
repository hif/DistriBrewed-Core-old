#!/usr/bin python
import threading
import time
import datetime
import json
from datetime import timedelta as timedelta
from distribrewed.core.defaults import *
from distribrewed.core.messages import *
from distribrewed.core.utils.coreutils import *
from distribrewed.core.workers.worker_measurement import WorkerMeasurement
import distribrewed.core.utils.logging as log
from distribrewed.core.comm.sessiondetail import SessionDetail
from distribrewed.core.comm.connection import WorkerConnection


MessageFunctions = (MessageInfo,
                    MessagePause,
                    MessageResume,
                    MessageReset,
                    MessageStop)


class BaseWorker(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.working = False
        self.name = name
        self.simulation = False
        self.ip = MessageServerIP
        self.master_port = 0
        self.worker_port = 0
        self.input_config = None
        self.output_config = None
        self.outputs = {}
        self.inputs = {}
        self.schedule = None
        self.enabled = False
        self.active = False
        self.pausing_all_devices = False
        self.current_hold_time = timedelta(minutes=0)
        self.hold_timer = None
        self.hold_pause_timer = None
        self.pause_time = 0.0
        self.debug_timer = datetime.date
        self.session_detail_id = 0
        self.connection = None

    def __str__(self):
        return 'Worker - [name:{0}, type:{1}, out:{2}, in:{3}]'. \
            format(self.name, str(self.__class__.__name__), len(self.output_config), len(self.input_config))

    def init_communication(self, ip, master_port, worker_port):
        self.ip = ip
        self.master_port = master_port
        self.worker_port = worker_port
        self.connection = WorkerConnection(self.ip, self.master_port, self.worker_port, self.name)

    def create_device_threads(self):
        for i in self.input_config:
            device = load_device(i, self, self.simulation)
            if device is None:
                return False
            device.run_device()
            self.inputs[i.name] = device
        for o in self.output_config:
            device = load_device(o, self, self.simulation)
            if device is None:
                return False
            self.outputs[o.name] = device
            device.run_device()
        return True

    def start_all_devices(self):
        for i in self.inputs.values():
            self.inputs[i.name] = i.start_device()
        for o in self.outputs.values():
            self.outputs[o.name] = o.start_device()

    def is_any_device_enabled(self):
        for i in self.inputs.values():
            if i.enabled:
                return True
        for o in self.outputs.values():
            if o.enabled:
                return True
        return False

    def is_device_enabled(self, name):
        if len(self.inputs) != 0:
            if self.inputs[name].enabled:
                return True
        if len(self.outputs) != 0:
            if self.outputs[name].enabled:
                return True
        return False

    def pause_all_devices(self):
        if self.pausing_all_devices:
            return
        self.pausing_all_devices = True
        while self.is_any_device_enabled():
            log.debug('Trying to pause all passive devices...')
            for i in self.inputs.values():
                i.pause_device()
            for o in self.outputs.values():
                o.pause_device()
            time.sleep(1)
        log.debug('All passive devices paused')
        self.pausing_all_devices = False

    def resume_all_devices(self):
        while self.pausing_all_devices:
            time.sleep(1)
        log.debug('Resuming all passive devices...')
        for i in self.inputs.values():
            i.resume_device()
        for o in self.outputs.values():
            o.resume_device()
        log.debug('All passive devices resumed')
        self.pausing_all_devices = False

    def stop_all_devices(self):
        for i in self.inputs.values():
            i.stop_device()
        for o in self.outputs.values():
            o.stop_device()

    def work(self, data):
        pass

    def run(self):
        if not self.create_device_threads():
            log.error('Unable to load all devices, shutting down', True)
        self.info()
        self.listen()

    def listen(self):
        self.enabled = True
        self.on_start()
        while self.enabled:
            log.debug("worker is listening", True)
            data = self.connection.check()
            if data is not None:
                self.receive(data)
            time.sleep(0)
        log.debug('Shutting down worker {0}'.format(self), True)

    def stop(self):
        self.stop_all_devices()
        self.on_stop()
        self.enabled = False

    def send_to_master(self, data):
        #log.debug('Sending to master - ' + data + " " + str(self.ip) + ":" + str(self.port), True)
        self.connection.send(data)

    def send_measurement(self, worker_measurement):
        message = WorkerMeasurement.serialize_message(worker_measurement)
        if message is None:
            return
        self.send_to_master(message)

    @staticmethod
    def generate_worker_measurement(worker, device):
        return WorkerMeasurement(worker.session_detail_id, worker.name, device.name)

    def work_time(self):
        if self.current_hold_time is None:
            return None
        return self.current_hold_time + self.pause_time

    def finish_time(self):
        if self.hold_timer is None:
            return None
        return datetime.datetime.utcnow() - self.hold_timer

    def remaining_time(self):
        finish = self.finish_time()
        if finish is None:
            return None
        work = self.work_time()
        if work is None:
            return None
        if finish > work:
            return timedelta()
        return work - finish

    def remaining_time_info(self):
        remaining = self.remaining_time()
        if remaining is None:
            return '-n/a-'
        if remaining.microseconds >= 500000:
            remaining -= timedelta(seconds=-1, microseconds=remaining.microseconds)
        else:
            remaining -= timedelta(microseconds=remaining.microseconds)
        return str(remaining)

    def receive(self, body):
        if body in MessageFunctions and hasattr(self, body):
            getattr(self, body)()
            return
        for json_obj in json.loads(body):
            print(json_obj)
            work_data = json_obj['fields']
            session_detail = SessionDetail()
            session_detail.id = json_obj['pk']
            session_detail.session = work_data['session']
            session_detail.index = work_data['index']
            session_detail.name = work_data['name']
            session_detail.worker_type = work_data['worker_type']
            session_detail.target = work_data['target']
            session_detail.hold_time = work_data['hold_time']
            session_detail.time_unit_seconds = work_data['time_unit_seconds']
            session_detail.notes = work_data['notes']
            session_detail.done = work_data['done']

            self.session_detail_id = session_detail.id
            self.work(session_detail)
            break   # only the first instance

    def info(self):
        log.debug('{0} is sending info to master'.format(self.name), True)
        if self.on_info():
            worker_type = '{0}.{1}'.format(self.__module__, self.__class__.__name__)
            message = MessageReady + MessageSplit + self.name + MessageSplit + worker_type
            for input_device in self.inputs.keys():
                message += (MessageSplit + input_device)
            for output_device in self.outputs.keys():
                message += (MessageSplit + output_device)
            self.send_to_master(message)
        else:
            self.report_error('Info failed')

    def done(self):
        log.debug('{0} is sending done to master'.format(self.name), True)
        if self.on_done():
            message = "{0}{1}{2}{3}{4}".format(MessageDone, MessageSplit,
                                               self.name, MessageSplit,
                                               str(self.session_detail_id))
            self.send_to_master(message)
        else:
            self.report_error('Done failed')

    def pause(self):
        log.debug('{0} is sending paused to master'.format(self.name), True)
        if not self.on_pause():
            self.report_error('Pause failed')

    def resume(self):
        log.debug('{0} is sending resumed to master'.format(self.name), True)
        if not self.on_resume():
            self.report_error('Resume failed')

    def reset(self):
        log.debug('{0} is resetting'.format(self.name), True)
        if self.on_reset():
            self.info()
        else:
            self.report_error('Reset failed')

    def report_error(self, err):
        log.error('{0}: {1}'.format(self.name, err), True)

    def is_done(self):
        if self.hold_timer is None:
            return False
        finish = self.finish_time()
        if finish is None:
            return False
        work = self.work_time()
        if work is None:
            return False
        if finish >= work:
            return True
        log.debug('Time until work done: {0}'.format(work - finish), True)
        return False

    def finish(self):
        try:
            self.pause_all_devices()
            self.working = False
            self.done()
            self.session_detail_id = 0
            return True
        except Exception as e:
            log.error('Error in cleaning up after work: {0}'.format(e.args[0]), True)
            return False

    def on_start(self):
        log.debug('Starting {0}'.format(self), True)

    def on_info(self):
        log.debug('Info {0}'.format(self), True)
        return True

    def on_done(self):
        log.debug('Done {0}'.format(self), True)
        return True

    def on_pause(self):
        log.debug('Pause {0}'.format(self), True)
        self.pause_all_devices()
        self.hold_pause_timer = datetime.datetime.utcnow()
        return True

    def on_resume(self):
        log.debug('Resume {0}'.format(self), True)
        self.pause_time += (datetime.datetime.utcnow() - self.hold_pause_timer)
        self.resume_all_devices()
        return True

    def on_reset(self):
        self.pause_all_devices()
        return True

    def on_stop(self):
        self.stop_all_devices()
        return True