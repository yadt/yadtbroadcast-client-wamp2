#!/usr/bin/env python

from __future__ import print_function
import sys
from twisted.internet import reactor
import logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


try:
    host = sys.argv[1]
    message = sys.argv[2]
except IndexError:
    print("Usage: {0} hostname message".format(sys.argv[0]))
    sys.exit(1)

sys.path.insert(0, "src/main/python")

from yadtbroadcastclient import WampBroadcaster


def flood(message):
    wamp._publish("topic", {"id":message})
    reactor.callLater(1, flood, message)

wamp = WampBroadcaster(host, "8080", "topic")

flood(message)
reactor.callLater(5, reactor.stop)
reactor.run()
