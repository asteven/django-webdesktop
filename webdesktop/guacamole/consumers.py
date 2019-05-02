import json
import logging
import pprint
import threading
import uuid

from django.conf import settings

#from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer

from .client import GuacamoleClient

logger = logging.getLogger('guacamole')
logger.setLevel(logging.DEBUG)

sockets = {}
sockets_lock = threading.RLock()
read_lock = threading.RLock()
write_lock = threading.RLock()
pending_read_request = threading.Event()


# TODO: may want to test with AsyncWebsocketConsumer?
class GuacamoleTunnelConsumer(WebsocketConsumer):
    def guac_reader(self):
        while self.keep_running:
            instruction = self.client.receive()
            logger.info('server-to-client %s', instruction)
            if instruction:
                self.send(instruction)
            else:
                break
        # End-of-instruction marker
        self.send('0.;')

    def connect(self):
        logger.debug('connect: %s', pprint.pformat(self.scope))

        self.client = GuacamoleClient(settings.GUACD_HOST, settings.GUACD_PORT,
            debug=True)

        # TODO: the connection info should come from DB/kv/wherever
        if settings.DESKTOP_PROTOCOL == 'vnc':
            self.client.handshake(protocol='vnc',
                             hostname=settings.VNC_HOST,
                             port=settings.VNC_PORT,
                             password=settings.VNC_PASSWORD)
        else:
            self.client.handshake(protocol='ssh',
                             hostname=settings.SSH_HOST,
                             port=settings.SSH_PORT,
                             username=settings.SSH_USER,
                             password=settings.SSH_PASSWORD)


        self.keep_running = True
        # FIXME: I have no clue if this thing is thread safe. It seems to work ok for one client.
        self.worker = threading.Thread(target=self.guac_reader, daemon=True)
        self.worker.start()
        self.accept(subprotocol='guacamole')

    def disconnect(self, close_code):
        logger.debug('disconnect: %s', close_code)
        self.keep_running = False
        self.worker.join()
        self.client.close()

    def receive(self, text_data):
        logger.debug('client-to-server: %s', text_data)
        self.client.send(text_data.encode())

