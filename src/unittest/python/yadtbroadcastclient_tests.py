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

    def test_should_flush_messages_after_connecting(self):
        self.mock_broadcaster.queue = [("topic1", "payload1"),
                                       ("topic2", "payload2")]
        self.mock_broadcaster.client = Mock()
        self.mock_broadcaster.on_session_open_handlers = []

        WampBroadcaster.onSessionOpen(self.mock_broadcaster)

        self.assertEqual(
            self.mock_broadcaster._publish.call_args_list,
            [
                call('topic1', 'payload1'),
                call('topic2', 'payload2')])

    def test_should_run_session_open_handlers_when_establishing_connection(self):
        handler_1 = Mock()
        handler_2 = Mock()
        self.mock_broadcaster.on_session_open_handlers = [handler_1, handler_2]
        self.mock_broadcaster.client = Mock()
        self.mock_broadcaster.queue = []

        WampBroadcaster.onSessionOpen(self.mock_broadcaster)

        handler_1.assert_called_with()
        handler_2.assert_called_with()
