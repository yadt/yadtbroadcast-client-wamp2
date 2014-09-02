#!/usr/bin/env python

from __future__ import print_function
import sys
from twisted.internet import reactor
import logging
logging.basicConfig()

try:
    host = sys.argv[1]
except IndexError:
    print("Usage: {0} hostname".format(sys.argv[0]))
    sys.exit(1)

sys.path.insert(0, "src/main/python")

from yadtbroadcastclient import WampBroadcaster

w = WampBroadcaster(host, "8080", "the_topic")
w.onEvent = print

w.connect()

reactor.run()
