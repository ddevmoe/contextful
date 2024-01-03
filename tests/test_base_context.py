import logging
from logging import LogRecord
from unittest import TestCase
from unittest.mock import Mock

from contextful import ContextLogger


class TestBaseContext(TestCase):
    def _get_logger(self, **logger_params) -> tuple[ContextLogger, Mock]:
        mock_handler = Mock()
        mock_handler.level = logging.INFO

        logger = ContextLogger(**logger_params)
        logger.addHandler(mock_handler)

        return logger, mock_handler

    def test_base_context__no_other_context_is_used__base_context_is_logged(self):
        # Arrange
        expected_context = {'base': True}
        expected_message = 'Some Message'
        logger, mock_handler = self._get_logger(base_context=expected_context)

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
        self.assertEqual(getattr(log_record, 'context', None), expected_context)

    def test_base_context__with_context_is_used__contexts_are_merged(self):
        # Arrange
        base_context = {'base': True}
        with_context = {'with': True}
        expected_context = {**base_context, **with_context}
        expected_message = 'Some Message'
        logger, mock_handler = self._get_logger(base_context=base_context)

        # Act
        with logger.context(with_context):
            logger.info(expected_message)

        # Assert
        handle_method_mock: Mock = mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        # We purposely avoid self.assertIsNotNone - https://github.com/microsoft/pyright/issues/2007
        assert log_record is not None, 'Expected log record to be generated'
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(getattr(log_record, 'context', None), expected_context)

    def test_base_context__inline_context_is_used__contexts_are_merged(self):
        # Arrange
        base_context = {'base': True}
        inline_context = {'inline': True}
        expected_context = {**base_context, **inline_context}
        expected_message = 'Some Message'
        logger, mock_handler = self._get_logger(base_context=base_context)

        # Act
        logger.info(expected_message, inline_context)

        # Assert
        handle_method_mock: Mock = mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        # We purposely avoid self.assertIsNotNone - https://github.com/microsoft/pyright/issues/2007
        assert log_record is not None, 'Expected log record to be generated'
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(getattr(log_record, 'context', None), expected_context)

    def test_base_context__with_context_is_used__base_context_is_overridden(self):
        # Arrange
        base_context = {'base': True}
        with_context = {'base': False, 'with': True}
        expected_context = with_context
        expected_message = 'Some Message'
        logger, mock_handler = self._get_logger(base_context=base_context)

        # Act
        with logger.context(with_context):
            logger.info(expected_message)

        # Assert
        handle_method_mock: Mock = mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        # We purposely avoid self.assertIsNotNone - https://github.com/microsoft/pyright/issues/2007
        assert log_record is not None, 'Expected log record to be generated'
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(getattr(log_record, 'context', None), expected_context)

    def test_base_context__inline_context_is_used__base_context_is_overridden(self):
        # Arrange
        base_context = {'base': True}
        inline_context = {'base': False, 'inline': True}
        expected_context = inline_context
        expected_message = 'Some Message'
        logger, mock_handler = self._get_logger(base_context=base_context)

        # Act
        logger.info(expected_message, inline_context)

        # Assert
        handle_method_mock: Mock = mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        # We purposely avoid self.assertIsNotNone - https://github.com/microsoft/pyright/issues/2007
        assert log_record is not None, 'Expected log record to be generated'
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(getattr(log_record, 'context', None), expected_context)

    def test_base_context__exclude_context_is_true__base_context_is_logged(self):
        # Arrange
        base_context = {'base': True}
        expected_context = base_context
        expected_message = 'Some Message'
        logger, mock_handler = self._get_logger(base_context=base_context)

        # Act
        logger.info(expected_message, exclude_context=True)

        # Assert
        handle_method_mock: Mock = mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        # We purposely avoid self.assertIsNotNone - https://github.com/microsoft/pyright/issues/2007
        assert log_record is not None, 'Expected log record to be generated'
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(getattr(log_record, 'context', None), expected_context)

    def test_base_context__exclude_context_is_true__with_context_is_used__only_base_context_is_logged(self):
        # Arrange
        base_context = {'base': True}
        with_context = {'with': True}
        expected_context = base_context
        expected_message = 'Some Message'
        logger, mock_handler = self._get_logger(base_context=base_context)

        # Act
        with logger.context(with_context):
            logger.info(expected_message, exclude_context=True)

        # Assert
        handle_method_mock: Mock = mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        # We purposely avoid self.assertIsNotNone - https://github.com/microsoft/pyright/issues/2007
        assert log_record is not None, 'Expected log record to be generated'
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(getattr(log_record, 'context', None), expected_context)
