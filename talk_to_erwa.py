#!/usr/bin/env python

from __future__ import print_function
import sys
from twisted.internet import reactor
import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

try:
    host = sys.argv[1]
except IndexError:
    print("Usage: {0} hostname".format(sys.argv[0]))
    sys.exit(1)

sys.path.insert(0, "src/main/python")

from yadtbroadcastclient import WampBroadcaster

w = WampBroadcaster(host, "8080", "the_topic")
w.onEvent = print

def spammy(counter, is_up):
    w.sendServiceChange({"fooservice": ("UP" if is_up else "DOWN")})
    w.sendFullUpdate({"counter": counter})
    counter = counter + 1
    reactor.callLater(5, spammy, counter, not is_up)


w.connect()
spammy(0, True)

reactor.run()
