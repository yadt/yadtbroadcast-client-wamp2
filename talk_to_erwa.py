#!/usr/bin/env python

from __future__ import print_function
import sys
from twisted.internet import reactor
import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

dummy_data = [[
    {u'services':
     [
         {u'state': u'up', u'uri': u'service://machine/frontend', u'name': u'frontend'},
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
w.onEvent = print


def spammy(counter, is_up):
    w.sendServiceChange([{'uri': "service://foo/bar", 'state': "UP" if is_up else "DOWN"}])
    w.sendFullUpdate(dummy_data)
    counter = counter + 1
    reactor.callLater(5, spammy, counter, not is_up)


w.connect()
spammy(0, True)

reactor.run()
