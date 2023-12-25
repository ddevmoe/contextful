import asyncio
import logging
from logging import LogRecord
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

from contextful import ContextLogger


class TestAsyncSupport(IsolatedAsyncioTestCase):
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

        assert log_record is not None, 'Expected log record to be generated'
        self.assertEqual(log_record.msg, expected_message)
        self.assertEqual(getattr(log_record, 'context', None), expected_context)

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

        assert first_log_record is not None, 'Expected first log record to be generated'
        self.assertEqual(first_log_record.msg, first_message, 'Expected first logger invocation to contain the first message')
        self.assertEqual(getattr(first_log_record, 'context', None), expected_context, 'Expected context to be the same for all concurrent invocations')

        assert second_log_record is not None, 'Expected second log record to be generated'
        self.assertEqual(second_log_record.msg, second_message, 'Expected second logger invocation to contain the second message')
        self.assertEqual(getattr(second_log_record, 'context', None), expected_context, 'Expected context to be the same for all concurrent invocations')

        assert third_log_record is not None, 'Expected third log record to be generated'
        self.assertEqual(third_log_record.msg, third_message, 'Expected third logger invocation to contain the third message')
        self.assertEqual(getattr(third_log_record, 'context', None), expected_context, 'Expected context to be the same for all concurrent invocations')

    async def test_multiple_async_method_calls__different_contexts__contexts_do_not_interfere_with_each_other(self):
        # Arrange
        parent_context = {'parent': True}

        first_message = 'first'
        first_context = {'child': 'first'}
        expected_first_context = {**parent_context, **first_context}
        async def first_child():
            with self.logger.context(first_context):
                await asyncio.sleep(0.1)  # first_child is invoked first, but purposely isn't the first to fire it's log
                await self._log_test_helper(first_message)

        second_message = 'second'
        second_context = {'child': 'second'}
        expected_second_context = {**parent_context, **second_context}
        async def second_child():
            with self.logger.context(second_context):
                await self._log_test_helper(second_message)

        # Act
        with self.logger.context(parent_context):
            await asyncio.gather(first_child(), second_child())

        # Assert
        handle_method_mock: Mock = self.mock_handler.handle
        invocations = handle_method_mock.call_args_list
        self.assertEqual(len(invocations), 2, 'Expected handle method to be invoked 2 times')

        # first_child's logger invocation is purposely delayed using asyncio.sleep call (`second_child` should have been run before `first_child`)
        second_invocation, first_invocation = invocations
        first_log_record: LogRecord | None = next(iter(first_invocation.args), None)
        second_log_record: LogRecord | None = next(iter(second_invocation.args), None)

        assert first_log_record is not None, 'Expected first log record to be generated'
        self.assertEqual(first_log_record.msg, first_message, 'Expected first logger invocation to contain the first message')
        self.assertEqual(getattr(first_log_record, 'context', None), expected_first_context, 'Expected first context to contain the parent and the first child\'s context')

        assert second_log_record is not None, 'Expected second log record to be generated'
        self.assertEqual(second_log_record.msg, second_message, 'Expected second logger invocation to contain the second message')
        self.assertEqual(getattr(second_log_record, 'context', None), expected_second_context, 'Expected second context to contain the parent and the first child\'s second')
