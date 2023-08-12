import logging
from logging import LogRecord
from unittest import TestCase
from unittest.mock import Mock

from contextful import ContextLogger


class TestMultiContextDefinitions(TestCase):
    def setUp(self) -> None:
        self.mock_handler = Mock()
        self.mock_handler.level = logging.INFO

        self.logger = ContextLogger()
        self.logger.addHandler(self.mock_handler)

    def test_multiple_contexts__contexts_are_logged_in_order(self):
        # Arrange
        first_message = 'first'
        first_context = {'first_context': True}

        second_message = 'second'
        second_context = {'second_context': True}

        # Act
        with self.logger.context(first_context):
            self.logger.info(first_message)

        with self.logger.context(second_context):
            self.logger.info(second_message)

        # Assert
        handle_method_mock: Mock = self.mock_handler.handle
        invocations = handle_method_mock.call_args_list
        self.assertEqual(len(invocations), 2, 'Expected handle method to be invoked 2 times')

        first_invocation, second_invocation = invocations
        first_log_record: LogRecord | None = next(iter(first_invocation.args), None)
        second_log_record: LogRecord | None = next(iter(second_invocation.args), None)

        self.assertEqual(first_log_record.msg, first_message, 'Expected first logger invocation to contain the first message')
        self.assertEqual(first_log_record.context, first_context, 'Expected second logger invocation to contain the first context')

        self.assertEqual(second_log_record.msg, second_message, 'Expected second logger invocation to contain the second message')
        self.assertEqual(second_log_record.context, second_context, 'Expected second logger invocation to contain the second context')