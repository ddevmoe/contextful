import logging
from logging import LogRecord
from unittest import TestCase
from unittest.mock import Mock

from contextful import ContextLogger


class TestContext(TestCase):
    def setUp(self) -> None:
        self.mock_handler = Mock()
        self.mock_handler.level = logging.DEBUG

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

        # We purposely avoid self.assertIsNotNone - https://github.com/microsoft/pyright/issues/2007
        assert log_record is not None, 'Expected log record to be generated'
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(getattr(log_record, 'context', None), expected_context)

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

        assert log_record is not None, 'Expected log record to be generated'
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(getattr(log_record, 'context', None), expected_context)

    def test_context_existed__context_does_not_persist(self):
        # Arrange
        first_message = 'first'
        first_context = {'some_data': True}

        second_message = 'second'

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

        assert first_log_record is not None, 'Expected first log record to be generated'
        self.assertEqual(first_log_record.msg, first_message)
        self.assertEqual(getattr(first_log_record, 'context', None), first_context)

        assert second_log_record is not None, 'Expected second log record to be generated'
        self.assertEqual(second_log_record.msg, second_message)
        self.assertFalse(hasattr(second_log_record, 'context'), 'Expected invocation outside of context to contain no context')

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

        assert log_record is not None, 'Expected log record to be generated'
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(getattr(log_record, 'context', None), expected_context)

    #region Log Levels Sanity

    def test_level_debug(self):
        # Arrange
        expected_message = 'Debug message'
        expected_context = {'tested_level': 'DEBUG'}

        # Act
        with self.logger.context(expected_context):
            self.logger.debug(expected_message)

        # Assert
        handle_method_mock: Mock = self.mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        assert log_record is not None, 'Expected debug log level to generate a record'
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(getattr(log_record, 'context', None), expected_context)

    def test_level_info(self):
        # Arrange
        expected_message = 'Info message'
        expected_context = {'tested_level': 'INFO'}

        # Act
        with self.logger.context(expected_context):
            self.logger.info(expected_message)

        # Assert
        handle_method_mock: Mock = self.mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        assert log_record is not None, 'Expected info log level to generate a record'
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(getattr(log_record, 'context', None), expected_context)

    def test_level_warning(self):
        # Arrange
        expected_message = 'Warning message'
        expected_context = {'tested_level': 'WARNING'}

        # Act
        with self.logger.context(expected_context):
            self.logger.warning(expected_message)

        # Assert
        handle_method_mock: Mock = self.mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        assert log_record is not None, 'Expected warning log level to generate a record'
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(getattr(log_record, 'context', None), expected_context)

    def test_level_error(self):
        # Arrange
        expected_message = 'Error message'
        expected_context = {'tested_level': 'ERROR'}

        # Act
        with self.logger.context(expected_context):
            self.logger.error(expected_message)

        # Assert
        handle_method_mock: Mock = self.mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        assert log_record is not None, 'Expected error log level to generate a record'
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(getattr(log_record, 'context', None), expected_context)

    def test_level_critical(self):
        # Arrange
        expected_message = 'Critical message'
        expected_context = {'tested_level': 'CRITICAL'}

        # Act
        with self.logger.context(expected_context):
            self.logger.critical(expected_message)

        # Assert
        handle_method_mock: Mock = self.mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        assert log_record is not None, 'Expected critical log level to generate a record'
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(getattr(log_record, 'context', None), expected_context)

    #endregion
