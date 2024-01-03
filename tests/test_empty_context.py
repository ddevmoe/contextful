import logging
from logging import LogRecord
from unittest import TestCase
from unittest.mock import Mock

from contextful import ContextLogger


class TestContext(TestCase):
    def _get_logger(self, **logger_params) -> tuple[ContextLogger, Mock]:
        mock_handler = Mock()
        mock_handler.level = logging.INFO

        logger = ContextLogger(**logger_params)
        logger.addHandler(mock_handler)

        return logger, mock_handler

    def test_context__always_set_context_is_false__no_context_provided__context_is_unset(self):
        # Arrange
        logger, mock_handler = self._get_logger(always_set_context=False)
        expected_message = 'Message'

        # Act
        logger.info(expected_message)

        # Assert
        handle_method_mock: Mock = mock_handler.handle
        handle_method_mock.assert_called_once()
        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        assert log_record is not None, 'Expected log record to be generated'
        self.assertEqual(log_record.msg, expected_message)
        self.assertFalse(hasattr(log_record, 'context'), 'Expected log record to not contain a context attribute')

    def test_context__always_set_context_is_true__no_context_provided__context_is_empty_dict(self):
        # Arrange
        logger, mock_handler = self._get_logger(always_set_context=True)
        expected_message = 'Some Message'
        expected_context = {}

        # Act
        logger.info(expected_message)

        # Assert
        handle_method_mock: Mock = mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        # We purposely avoid self.assertIsNotNone - https://github.com/microsoft/pyright/issues/2007
        assert log_record is not None, 'Expected log record to be generated'
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(getattr(log_record, 'context', None), expected_context, 'Expected context to be an empty dict')

    def test_context__always_set_context_is_true__context_provided__context_is_set_correctly(self):
        # Arrange
        logger, mock_handler = self._get_logger(always_set_context=True)
        expected_message = 'Some Message'
        expected_context = {'some_context': True}

        # Act
        with logger.context(expected_context):
            logger.info(expected_message)

        # Assert
        handle_method_mock: Mock = mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        # We purposely avoid self.assertIsNotNone - https://github.com/microsoft/pyright/issues/2007
        assert log_record is not None, 'Expected log record to be generated'
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(getattr(log_record, 'context', None), expected_context, 'Expected context to be an empty dict')
