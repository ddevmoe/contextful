import logging
import uuid
from typing import Callable

from contextlib import AbstractContextManager
from contextvars import ContextVar, Token


class LogContext(AbstractContextManager):
    def __init__(
        self,
        data: dict,
        context_token: Token,
        cleanup_hook: Callable[['LogContext'], None],
        id_: str | None = None,
    ):
        self.id = id_ or str(uuid.uuid4())
        self.data = data
        self.context_token = context_token
        self._cleanup_hook = cleanup_hook

    def __enter__(self, *args, **kwargs):
        return super().__enter__(*args, **kwargs)

    def __exit__(self, *args, **kwargs) -> bool | None:
        self._cleanup_hook(self)
        return super().__exit__(*args, **kwargs)


_global_context = ContextVar('context_logger_asyncio_context_store', default={})


class ContextLogger(logging.Logger):
    def __init__(
        self,
        name: str = 'main',
        level: int = logging.NOTSET,
        always_set_context: bool = False,
    ):
        """
        always_set_context - Ensure `LogRecord` instances always have a `context` attribute set to an empty `dict`, even when no context is provided.
        """

        self._always_set_context = always_set_context
        super().__init__(name, level)

    def _log(self, level: int, msg: object, context: dict | None = None, *args, **kwargs):
        if not self.isEnabledFor(level):
            return

        finalized_context = {**_global_context.get(), **(context or {})}

        # If there's both the global context and the current log's context are empty - log without context
        if not finalized_context and not self._always_set_context:
            super()._log(level, msg, args, **kwargs)
            return

        # If extra isn't utilized by the current log, add a new one with our context mounted on top
        if 'extra' not in kwargs:
            super()._log(level, msg, args, **kwargs, extra={'context': finalized_context})
            return

        extra = kwargs.get('extra', {})
        if 'context' in extra:
            raise ValueError('Logging "extra" dict must not contain a key named "context" as it is reserved for ContexLogger\'s usage.')
        extra['context'] = finalized_context

        super()._log(level, msg, args, **kwargs)

    def _remove_context(self, log_context: LogContext):
        _global_context.reset(log_context.context_token)

    def context(self, context: dict) -> LogContext:
        current_context = _global_context.get()
        new_context = {**current_context, **context}
        context_token = _global_context.set(new_context)

        log_context = LogContext(context, context_token, self._remove_context)
        return log_context
