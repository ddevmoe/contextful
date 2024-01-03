import logging
from logging import LogRecord
from unittest import TestCase
from unittest.mock import Mock

from contextful import ContextLogger


class TestTopLevelFields(TestCase):
    def _get_logger(self, **logger_params) -> tuple[ContextLogger, Mock]:
        mock_handler = Mock()
        mock_handler.level = logging.INFO

        logger = ContextLogger(**logger_params)
        logger.addHandler(mock_handler)

        return logger, mock_handler

    def test_top_level_fields__fields_exist_on_log_record(self):
        # Arrange
        top_level_fields_context = {'field1': 'field1_value', 'field2': 'field2_value'}
        regular_fields_context = {'regular_field': True}
        context = {**regular_fields_context, **top_level_fields_context}
        expected_context = regular_fields_context
        top_level_fields = list(top_level_fields_context)
        expected_message = 'Some Message'
        logger, mock_handler = self._get_logger(top_level_fields=top_level_fields)

        # Act
        with logger.context(context):
            logger.info(expected_message)

        # Assert
        handle_method_mock: Mock = mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        # We purposely avoid self.assertIsNotNone - https://github.com/microsoft/pyright/issues/2007
        assert log_record is not None, 'Expected log record to be generated'
        self.assertEqual(log_record.msg, expected_message)

        for field, value in top_level_fields_context.items():
            self.assertEqual(getattr(log_record, field, None), value, f'Expected field "{field}" defined as top level to be attached to the generated log record')

        self.assertEqual(getattr(log_record, 'context', None), expected_context)

    def test_top_level_fields__fields_used_in_base_context__fields_exist_on_log_record(self):
        # Arrange
        top_level_fields_context = {'field1': 'field1_value', 'field2': 'field2_value'}
        regular_fields_context = {'regular_field': True}
        base_context = {**regular_fields_context, **top_level_fields_context}
        expected_context = regular_fields_context
        top_level_fields = list(top_level_fields_context)
        expected_message = 'Some Message'
        logger, mock_handler = self._get_logger(base_context=base_context, top_level_fields=top_level_fields)

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

        for field, value in top_level_fields_context.items():
            self.assertEqual(getattr(log_record, field, None), value, f'Expected field "{field}" defined as top level to be attached to the generated log record')

        self.assertEqual(getattr(log_record, 'context', None), expected_context)

    def test_top_level_fields__fields_used_in_with_context__fields_exist_on_log_record(self):
        # Arrange
        top_level_fields_context = {'field1': 'field1_value', 'field2': 'field2_value'}
        regular_fields_context = {'regular_field': True}
        with_context = {**regular_fields_context, **top_level_fields_context}
        expected_context = regular_fields_context
        top_level_fields = list(top_level_fields_context)
        expected_message = 'Some Message'
        logger, mock_handler = self._get_logger(top_level_fields=top_level_fields)

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

        for field, value in top_level_fields_context.items():
            self.assertEqual(getattr(log_record, field, None), value, f'Expected field "{field}" defined as top level to be attached to the generated log record')

        self.assertEqual(getattr(log_record, 'context', None), expected_context)

    def test_top_level_fields__fields_used_in_inline_context__fields_exist_on_log_record(self):
        # Arrange
        top_level_fields_context = {'field1': 'field1_value', 'field2': 'field2_value'}
        regular_fields_context = {'regular_field': True}
        inline_context = {**regular_fields_context, **top_level_fields_context}
        expected_context = regular_fields_context
        top_level_fields = list(top_level_fields_context)
        expected_message = 'Some Message'
        logger, mock_handler = self._get_logger(top_level_fields=top_level_fields)

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

        for field, value in top_level_fields_context.items():
            self.assertEqual(getattr(log_record, field, None), value, f'Expected field "{field}" defined as top level to be attached to the generated log record')

        self.assertEqual(getattr(log_record, 'context', None), expected_context)

    def test_top_level_fields__always_set_context_is_true__all_context_fields_are_top_level__context_is_empty_dict(self):
        # Arrange
        top_level_fields_context = {'field1': 'field1_value', 'field2': 'field2_value'}
        expected_context = {}
        top_level_fields = list(top_level_fields_context)
        expected_message = 'Some Message'
        logger, mock_handler = self._get_logger(top_level_fields=top_level_fields, always_set_context=True)

        # Act
        with logger.context(top_level_fields_context):
            logger.info(expected_message)

        # Assert
        handle_method_mock: Mock = mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        # We purposely avoid self.assertIsNotNone - https://github.com/microsoft/pyright/issues/2007
        assert log_record is not None, 'Expected log record to be generated'
        self.assertEqual(log_record.msg, expected_message)

        for field, value in top_level_fields_context.items():
            self.assertEqual(getattr(log_record, field, None), value, f'Expected field "{field}" defined as top level to be attached to the generated log record')

        self.assertEqual(getattr(log_record, 'context', None), expected_context)

    def test_top_level_fields__always_set_context_is_false__all_context_fields_are_top_level__context_is_unset(self):
        # Arrange
        top_level_fields_context = {'field1': 'field1_value', 'field2': 'field2_value'}
        top_level_fields = list(top_level_fields_context)
        expected_message = 'Some Message'
        logger, mock_handler = self._get_logger(top_level_fields=top_level_fields, always_set_context=False)

        # Act
        with logger.context(top_level_fields_context):
            logger.info(expected_message)

        # Assert
        handle_method_mock: Mock = mock_handler.handle
        handle_method_mock.assert_called_once()

        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        # We purposely avoid self.assertIsNotNone - https://github.com/microsoft/pyright/issues/2007
        assert log_record is not None, 'Expected log record to be generated'
        self.assertEqual(log_record.msg, expected_message)

        for field, value in top_level_fields_context.items():
            self.assertEqual(getattr(log_record, field, None), value, f'Expected field "{field}" defined as top level to be attached to the generated log record')

        self.assertFalse(hasattr(log_record, 'context'), 'Expected log record to not contain a context since all fields were defined as top level')
