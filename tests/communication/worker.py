import time

import distribrewed.core.utils.logging as log
from distribrewed.core.comm.connection import WorkerConnection
from distribrewed.core.defaults import MessageServerIP, MessageServerWorkerPort
from distribrewed.core.defaults import MessageServerMasterPort

ping_count = 5

if __name__ == "__main__":
    worker = WorkerConnection(
        MessageServerIP,
        MessageServerMasterPort,
        MessageServerWorkerPort,
        'TestWorker'
    )

    count = 0
    while count < ping_count:
        log.info('Trying to ping master...')
        worker.send("PING")
        count += 1
        time.sleep(0.5)
    log.info('Worker ping sent: {0}'.format(count))
