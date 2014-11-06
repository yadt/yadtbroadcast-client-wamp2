from unittest import TestCase

from mock import Mock, call

from yadtbroadcastclient import WampBroadcaster


class WampBroadcasterTests(TestCase):

    def test_should_queue_messages_when_not_connected(self):
        mock_broadcaster = Mock(WampBroadcaster)
        mock_broadcaster.target = "any_wamp_topic"
        mock_broadcaster.logger = Mock()
        mock_broadcaster.queue = Mock()
        mock_broadcaster._check_connection.return_value = False

        WampBroadcaster._sendEvent(mock_broadcaster, "any-id", {"any-key": "any-value"})
        WampBroadcaster._sendEvent(mock_broadcaster, "other-id", {"other-key": "other-value"})

        self.assertEqual(mock_broadcaster.queue.append.call_args_list,
                         [call(('any_wamp_topic',
                                {'payload': {'any-key': 'any-value'},
                                 'type': 'event',
                                 'id': 'any-id',
                                 'tracking_id': None,
                                 'target': 'any_wamp_topic'})),
                          call(('any_wamp_topic',
                                {'payload': {'other-key': 'other-value'},
                                 'type': 'event',
                                 'id': 'other-id',
                                 'tracking_id': None,
                                 'target': 'any_wamp_topic'}))])
