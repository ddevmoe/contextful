import logging
from logging import LogRecord
from unittest import TestCase
from unittest.mock import Mock

from contextful import ContextLogger


class TestInlineContext(TestCase):
    def setUp(self) -> None:
        self.mock_handler = Mock()
        self.mock_handler.level = logging.INFO

        self.logger = ContextLogger()
        self.logger.addHandler(self.mock_handler)

    def test_inline_context__context_with_inline_context__contexts_are_merged(self):
        # Arrange
        context = {'context': True, 'manager_says': 'from manager'}
        inline_context = {'inline': True, 'inline_says': 'from inline'}
        expected_context = {**context, **inline_context}
        expected_message = 'inline message'

        # Act
        with self.logger.context(context):
            self.logger.info(expected_message, context=inline_context)

        # Assert
        handle_method_mock: Mock = self.mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        # We purposely avoid self.assertIsNotNone - https://github.com/microsoft/pyright/issues/2007
        assert log_record is not None, 'Expected log record to be generated'
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(getattr(log_record, 'context', None), expected_context)

    def test_inline_context__context_with_inline_context__context_overridden_by_inline_context(self):
        # Arrange
        context = {'context': 'defined at manager', 'param': 'value1'}
        inline_context = {'context': 'defined inline', 'param': 'value2'}
        expected_context = inline_context
        expected_message = 'inline message'

        # Act
        with self.logger.context(context):
            self.logger.info(expected_message, context=inline_context)

        # Assert
        handle_method_mock: Mock = self.mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        # We purposely avoid self.assertIsNotNone - https://github.com/microsoft/pyright/issues/2007
        assert log_record is not None, 'Expected log record to be generated'
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(getattr(log_record, 'context', None), expected_context)

    def test_inline_context__empty_context_with_inline_context__inline_context_logged(self):
        # Arrange
        context = {}
        inline_context = {'inline': 'defined inline'}
        expected_context = inline_context
        expected_message = 'inline message'

        # Act
        with self.logger.context(context):
            self.logger.info(expected_message, context=inline_context)

        # Assert
        handle_method_mock: Mock = self.mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        # We purposely avoid self.assertIsNotNone - https://github.com/microsoft/pyright/issues/2007
        assert log_record is not None, 'Expected log record to be generated'
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(getattr(log_record, 'context', None), expected_context)


class TestExcludeContext(TestCase):
    def _get_logger(self, logger_params: dict) -> tuple[ContextLogger, Mock]:
        mock_handler = Mock()
        mock_handler.level = logging.INFO

        logger = ContextLogger(**logger_params)
        logger.addHandler(mock_handler)

        return logger, mock_handler

    def test_exclude_context__context_exists_exclude_true__context_is_unset(self):
        # Arrange
        logger, mock_handler = self._get_logger({})
        context = {'context': True}
        expected_message = 'lonely message'

        # Act
        with logger.context(context):
            logger.info(expected_message, exclude_context=True)

        # Assert
        handle_method_mock: Mock = mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        # We purposely avoid self.assertIsNotNone - https://github.com/microsoft/pyright/issues/2007
        assert log_record is not None, 'Expected log record to be generated'
        self.assertEqual(log_record.msg, expected_message)
        self.assertFalse(hasattr(log_record, 'context'), 'Expected log record to not contain a context attribute')

    def test_exclude_context__context_exists_exclude_true_always_set_context_true__context_is_empty_dict(self):
        # Arrange
        logger, mock_handler = self._get_logger({'always_set_context': True})
        context = {'context': True}
        expected_context = {}
        expected_message = 'lonely message'

        # Act
        with logger.context(context):
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
