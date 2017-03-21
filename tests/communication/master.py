import time

import distribrewed.core.utils.logging as log
from distribrewed.core.comm.connection import MasterConnection
from distribrewed.core.defaults import MessageServerIP, MessageServerMasterPort, MessageServerWorkerPort
from distribrewed.core.messages import MessageInfo

ping_count = 5

if __name__ == "__main__":
    conn = MasterConnection(
        MessageServerIP,
        MessageServerMasterPort,
        MessageServerWorkerPort
    )
    conn.broadcast(MessageInfo)
    count = 0
    timeout = time.time() + 10  # 10 sec
    log.info('Master waiting...')
    while count < ping_count and time.time() < timeout:
        data = conn.check()
        if data is not None:
            log.debug('Received: {0}'.format(data))
            count += 1
        time.sleep(0)
    log.info('Worker ping received: {0}'.format(count))
