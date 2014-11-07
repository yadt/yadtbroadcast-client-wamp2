from unittest import TestCase

from mock import Mock, call

from yadtbroadcastclient import WampBroadcaster


class WampBroadcasterReconnectionTests(TestCase):

    def setUp(self):
        self.mock_broadcaster = Mock(WampBroadcaster)
        self.mock_broadcaster.target = "any_wamp_topic"
        self.mock_broadcaster.logger = Mock()
        self.mock_broadcaster.queue = Mock()

    def test_should_queue_messages_when_not_connected(self):
        self.mock_broadcaster._check_connection.return_value = False

        WampBroadcaster._publish(self.mock_broadcaster, "any-topic", {"any-key": "any-value"})
        WampBroadcaster._publish(self.mock_broadcaster, "other-topic", {"other-key": "other-value"})

        self.assertEqual(self.mock_broadcaster.queue.append.call_args_list,
                         [call(('any-topic', {'any-key': 'any-value'})),
                          call(('other-topic', {'other-key': 'other-value'}))])

