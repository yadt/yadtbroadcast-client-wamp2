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


received = []
timeout_in_seconds = 10
expected_event = {"id": message}
global exit_code
exit_code = 1


def onEvent(event):
    logger.info("Got event %s" % str(event))
    try:
        verify_if_is_expected_event(event)
    except Exception as e:
        logger.error(e)


def verify_if_is_expected_event(event):
    if expected_event == event:
        logger.info("Success: found target event %s" % expected_event)
        global exit_code
        exit_code = 0
        reactor.stop()
    else:
        logger.info("Expected message not yet found")


def timeout(timeout_in_seconds):
    logger.error("Timed out after %d seconds" % timeout_in_seconds)
    reactor.stop()


wamp = WampBroadcaster(host, "8080", "topic")
wamp.onEvent = onEvent

logger.info("Waiting %d seconds for target event %s" % (timeout_in_seconds, expected_event))

reactor.callLater(timeout_in_seconds, timeout, timeout_in_seconds)
reactor.run()
sys.exit(exit_code)
