import logging
import socket
import sys


lock_socket = None


def is_lock_free():
    global lock_socket
    lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    lock_id = "cbsteh.pysawitweb-nyt"
    try:
        lock_socket.bind('\0' + lock_id)
        logging.info("Acquired lock %r" % (lock_id,))
        return True
    except socket.error:
        logging.info("Failed to acquire lock %r" % (lock_id,))
        return False


logging.basicConfig(filename="nyt.log", level=logging.INFO)
if not is_lock_free():
    sys.exit()


from datetime import datetime
from subprocess import call

dt = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
logging.info('>>> Started at {} >>>'.format(dt))
try:
    py36 = '/home/cbsteh/.virtualenvs/pysawitweb-venv/bin/python3.6'
    managepy = '/home/cbsteh/pysawitweb/manage.py'
    arg = 'notifymail'
    call([py36, managepy, arg])
except Exception as e:
    logging.error(e, exc_info=True)
