#!/usr/bin/env python

from __future__ import print_function

import sys
import logging
import unittest
import json
from functools import partial

import requests
from twisted.internet import reactor
reactor.exit_code = 1

FORMAT = "%(asctime)-15s %(name)10s %(levelname)s %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.getLogger("requests").setLevel(logging.ERROR)

dummy_data = [[
    {u'services':
     [
         {u'state': u'down', u'uri': u'service://machine/frontend', u'name': u'frontend'},
         {u'state': u'down', u'uri': u'service://machine/iptables', u'name': u'iptables'},
         {u'state': u'up', u'uri': u'service://machine/middleservice1', u'name': u'middleservice1'},
         {u'state': u'up', u'uri': u'service://machine/middleservice2', u'name': u'middleservice2'},
         {u'state': u'up', u'uri': u'service://machine/backservice', u'name': u'backservice'},
         {u'state': u'up', u'uri': u'service://machine/docker', u'name': u'docker'}
     ],
     u'artefacts': [
         {u'current': u'0.9.1-42.el9.x86_64', u'uri': u'artefact://machine/ConsoleKit-libs', u'name': u'ConsoleKit-libs'},
         {u'current': u'1.3.10-33.el9.x86_64', u'uri': u'artefact://machine/zsh', u'name': u'zsh'}
     ],
     u'name': u'machine'},
    {u'services':
     [
         {u'state': u'up', u'uri': u'service://host2/frontend', u'name': u'frontend'},
         {u'state': u'down', u'uri': u'service://host2/iptables', u'name': u'iptables'},
         {u'state': u'up', u'uri': u'service://host2/middleservice1', u'name': u'middleservice1'},
         {u'state': u'up', u'uri': u'service://host2/middleservice2', u'name': u'middleservice2'},
         {u'state': u'up', u'uri': u'service://host2/backservice', u'name': u'backservice'},
         {u'state': u'up', u'uri': u'service://host2/docker', u'name': u'docker'}
     ],
     u'artefacts': [
         {u'current': u'0.9.1-42.el9.x86_64', u'uri': u'artefact://host2/ConsoleKit-libs', u'name': u'ConsoleKit-libs'},
         {u'current': u'1.3.10-33.el9.x86_64', u'uri': u'artefact://host2/zsh', u'name': u'zsh'}
     ],
        u'name': u'host2'},

]]

try:
    host = sys.argv[1]
except IndexError:
    print("Usage: {0} hostname".format(sys.argv[0]))
    sys.exit(1)


sys.path.insert(0, "src/main/python")
from yadtbroadcastclient import WampBroadcaster
from time import time

test_id = str(int(time()))

w = WampBroadcaster(host, "8080", test_id)
w.onEvent = partial(print, "Got event ")


def connected():
    reactor.connected = True


def send_full_update_and_service_change():
    w.sendServiceChange([{'uri': "service://foo/bar", 'state': "UP"}])
    w.sendFullUpdate(dummy_data)
    reactor.callLater(5, reactor.stop)


def ensure_test_data_is_present():
    tc = unittest.TestCase('__init__')
    logger.info("Checking full target API..")
    target_status = requests.get("http://%s:8080/api/v1/targets/%s/full" % (host, test_id))
    tc.assertEqual(target_status.status_code, 200)
    logger.info("Status ok, checking contents..")
    actual_stored_data = json.loads(target_status.text)
    expected_stored_data = [{u'services': [{u'state': u'down', u'name': u'frontend'}, {u'state': u'down', u'name': u'iptables'}, {u'state': u'up', u'name': u'middleservice1'}, {u'state': u'up', u'name': u'middleservice2'}, {u'state': u'up', u'name': u'backservice'}, {u'state': u'up', u'name': u'docker'}], u'host': u'machine', u'artefacts': [{u'version': u'0.9.1-42.el9.x86_64', u'name': u'ConsoleKit-libs'}, {u'version': u'1.3.10-33.el9.x86_64', u'name': u'zsh'}]}, {u'services': [{u'state': u'up', u'name': u'frontend'}, {u'state': u'down', u'name': u'iptables'}, {u'state': u'up', u'name': u'middleservice1'}, {u'state': u'up', u'name': u'middleservice2'}, {u'state': u'up', u'name': u'backservice'}, {u'state': u'up', u'name': u'docker'}], u'host': u'host2', u'artefacts': [{u'version': u'0.9.1-42.el9.x86_64', u'name': u'ConsoleKit-libs'}, {u'version': u'1.3.10-33.el9.x86_64', u'name': u'zsh'}]}]
    tc.assertEqual(expected_stored_data, actual_stored_data)
    reactor.exit_code = 0


def timeout(nr_seconds):
    print("Trying timeout")
    if not getattr(reactor, "connected", default=False):
        logger.error("Timed out after %d seconds waiting for connection" % nr_seconds)
        reactor.exit_code = 1
        reactor.stop()


w.addOnSessionOpenHandler(connected)
send_full_update_and_service_change()
reactor.callLater(10, timeout, 10)
reactor.run()

ensure_test_data_is_present()
sys.exit(reactor.exit_code)
