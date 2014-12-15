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


w = WampBroadcaster(host, "8080", "foo")
w.onEvent = partial(print, "Got event ")


def connected():
    reactor.connected = True

def send_full_update_and_service_change():
    w.sendServiceChange([{'uri': "service://foo/bar", 'state': "UP"}])
    w.sendFullUpdate(dummy_data)
    reactor.callLater(5, reactor.stop)


def clear_test_data():
    delete_triple("services", "foo", "bar")
    delete_triple("targets", "foo", "hosts")


def delete_triple(type_, bucket, key):
    response = requests.delete("http://%s:8098/types/%s/buckets/%s/keys/%s" % (host, type_, bucket, key))
    logger.info("Deleting %s/%s/%s: %s" % (type_, bucket, key, response))


def ensure_test_data_is_present():
    tc = unittest.TestCase('__init__')
    logger.info("Checking full target API..")
    foo_status = requests.get("http://%s:8080/api/v1/targets/foo/full" % host)
    tc.assertEqual(foo_status.status_code, 200)
    logger.info("Checking target keys..")
    foo_hosts = requests.get("http://%s:8098/types/targets/buckets/foo/keys/hosts" % host)
    tc.assertEqual(foo_hosts.text, "machine\nhost2")
    logger.info("Checking service keys")
    bar_service_state = requests.get("http://%s:8098/types/services/buckets/foo/keys/bar" % host)
    tc.assertEqual(bar_service_state.text, "UP")
    reactor.exit_code = 0


def timeout(nr_seconds):
    print("Trying timeout")
    if not getattr(reactor, "connected", default=False):
        logger.error("Timed out after %d seconds waiting for connection" % nr_seconds)
        reactor.exit_code = 1
        reactor.stop()


clear_test_data()

w.addOnSessionOpenHandler(connected)
send_full_update_and_service_change()
reactor.callLater(10, timeout, 10)
reactor.run()

ensure_test_data_is_present()
sys.exit(reactor.exit_code)
