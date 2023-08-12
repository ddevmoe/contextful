import asyncio
import logging
from logging import LogRecord
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

from contextful import ContextLogger


class TestMultiContextDefinitions(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_handler = Mock()
        self.mock_handler.level = logging.INFO
        self.logger = ContextLogger()
        self.logger.addHandler(self.mock_handler)

    async def _log_test_helper(self, message: str):
        self.logger.info(message)

    async def test_context_outside_async_method__context_is_logged_inside_async_method(self):
        # Arrange
        expected_message = 'Message'
        expected_context = {'a': 1001}

        # Act
        with self.logger.context(expected_context):
            await self._log_test_helper(expected_message)

        # Assert
        handle_method_mock: Mock = self.mock_handler.handle
        handle_method_mock.assert_called_once()
        invocation_arguments = handle_method_mock.call_args[0]
        log_record: LogRecord | None = next(iter(invocation_arguments), None)

        self.assertEqual(log_record.context, expected_context)
        self.assertEqual(log_record.msg, expected_message)

    async def test_context_outside_async_method__multiple_asynchronous_invocations__context_is_logged_on_every_call(self):
        # Arrange
        first_message = 'first'
        second_message = 'second'
        third_message = 'third'
        expected_context = {'a': 1001}

        # Act
        with self.logger.context(expected_context):
            await asyncio.gather(
                self._log_test_helper(first_message),
                self._log_test_helper(second_message),
                self._log_test_helper(third_message),
            )

        # Assert
        handle_method_mock: Mock = self.mock_handler.handle
        invocations = handle_method_mock.call_args_list
        self.assertEqual(len(invocations), 3, 'Expected handle method to be invoked 3 times')

        first_invocation, second_invocation, third_invocation = invocations
        first_log_record: LogRecord | None = next(iter(first_invocation.args), None)
        second_log_record: LogRecord | None = next(iter(second_invocation.args), None)
        third_log_record: LogRecord | None = next(iter(third_invocation.args), None)

        self.assertEqual(first_log_record.msg, first_message, 'Expected first logger invocation to contain the first message')
        self.assertEqual(first_log_record.context, expected_context, 'Expected context to be the same for all concurrent invocations')

        self.assertEqual(second_log_record.msg, second_message, 'Expected second logger invocation to contain the second message')
        self.assertEqual(second_log_record.context, expected_context, 'Expected context to be the same for all concurrent invocations')

        self.assertEqual(third_log_record.msg, third_message, 'Expected third logger invocation to contain the third message')
        self.assertEqual(third_log_record.context, expected_context, 'Expected context to be the same for all concurrent invocations')

    async def test_multiple_async_method_calls__different_contexts__contexts_do_not_overwrite_each_other(self):
        # Arrange
        
        # Act
        
        # Assert
        pass
