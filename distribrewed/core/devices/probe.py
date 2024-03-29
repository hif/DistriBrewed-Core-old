#!/usr/bin python
import time

import distribrewed.core.utils.logging as log

from distribrewed.core.devices.device import Device, DEVICE_DEBUG_CYCLE_TIME


class Probe(Device):
    def __init__(self, config, owner=None, simulation=False):
        self.test_temperature = 0.0
        Device.__init__(self, config, owner, simulation)

    def init(self):
        # TODO: Implment
        pass

    def register(self):
        if self.simulation:
            return True
        log.error("Can not register probe at \"{0}\", try to run \"sudo modprobe w1-gpio && sudo modprobe w1_therm\" in commandline or check your probe connections".format(self.io))

    def write(self, value):
        # TODO:Implment
        pass

    def read(self):
        if self.simulation:
            return self.test_temperature
        with self.read_write_lock:
            fo = open(self.io, mode='r')
            probe_crc = fo.readline()[-4:].rstrip()
            #log.debug(probe_crc)
            if probe_crc != 'YES':
                log.debug('Temp reading wrong, do not update temp, wait for next reading')
            else:
                probe_heat = fo.readline().split('=')[1]
            temperature = float(probe_heat)/1000
            fo.close()
        return temperature

    def run_cycle(self):
        read_value = self.read()
        measured_value = float(read_value)
        self.do_callback(measured_value)
        if self.simulation:
            time.sleep(DEVICE_DEBUG_CYCLE_TIME)
        else:
            time.sleep(self.cycle_time)

