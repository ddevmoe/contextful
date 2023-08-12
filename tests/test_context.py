import logging
from logging import LogRecord
from unittest import TestCase
from unittest.mock import Mock

from contextful import ContextLogger


class TestContext(TestCase):
    def setUp(self) -> None:
        self.mock_handler = Mock()
        self.mock_handler.level = logging.INFO

        self.logger = ContextLogger()
        self.logger.addHandler(self.mock_handler)

    def test_context_is_logged(self):
        # Arrange
        expected_context = {'a': 'b'}
        expected_message = 'Some Message'

        # Act
        with self.logger.context(expected_context):
            self.logger.info(expected_message)

        # Assert
        handle_method_mock: Mock = self.mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(log_record.context, expected_context)

    def test_nested_context__all_hierarchies_are_logged(self):
        # Arrange
        first_context = {'first': True}
        second_context = {'second': True}
        third_context = {'third': True}
        expected_context = {**first_context, **second_context, **third_context}
        expected_message = 'A Message'

        # Act
        with self.logger.context(first_context):
            with self.logger.context(second_context):
                with self.logger.context(third_context):
                    self.logger.info(expected_message)

        # Assert
        handle_method_mock: Mock = self.mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(log_record.context, expected_context)

    def test_log_without_context__logs_message(self):
        # Arrange
        expected_message = 'Message'
        expected_context = {}

        # Act
        self.logger.info(expected_message)

        # Assert
        handle_method_mock: Mock = self.mock_handler.handle
        handle_method_mock.assert_called_once()
        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        self.assertEqual(log_record.context, expected_context)
        self.assertEqual(log_record.msg, expected_message)

    def test_context_existed__context_does_not_persist(self):
        # Arrange
        first_message = 'first'
        first_context = {'some_data': True}

        second_message = 'second'
        empty_context = {}

        # Act
        with self.logger.context(first_context):
            self.logger.info(first_message)

        self.logger.info(second_message)

        # Assert
        handle_method_mock: Mock = self.mock_handler.handle
        invocations = handle_method_mock.call_args_list
        self.assertEqual(len(invocations), 2, 'Expected handle method to be invoked 2 times')

        first_invocation, second_invocation = invocations
        first_log_record: LogRecord | None = next(iter(first_invocation.args), None)
        second_log_record: LogRecord | None = next(iter(second_invocation.args), None)

        self.assertEqual(first_log_record.msg, first_message)
        self.assertEqual(first_log_record.context, first_context)

        self.assertEqual(second_log_record.msg, second_message)
        self.assertEqual(second_log_record.context, empty_context, 'Expected invocation outside of context to contain no context')

    def _log_test_helper(self, message: str):
        self.logger.info(message)

    def test_log_in_nested_function_within_context__context_is_logged(self):
        # Arrange
        expected_message = 'Some Message'
        expected_context = {'a': 'b'}

        # Act
        with self.logger.context(expected_context):
            self._log_test_helper(expected_message)

        # Assert
        handle_method_mock: Mock = self.mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(log_record.context, expected_context)