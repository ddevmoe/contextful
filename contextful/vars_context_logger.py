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
        id_: str = None,
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
    def __init__(self, name: str = 'main', level: int = logging.NOTSET):
        super().__init__(name, level)

    def _log(self, level: int, msg: object, *args, extra: dict | None = None, **kwargs) -> None:
        current_context = _global_context.get()
        context_wrapper = {'context': current_context}
        return super()._log(level, msg, *args, extra=context_wrapper, **kwargs)

    def _remove_context(self, log_context: LogContext):
        _global_context.reset(log_context.context_token)

    def context(self, extra: dict) -> LogContext:
        current_context = _global_context.get()
        new_context = {**current_context, **extra}
        context_token = _global_context.set(new_context)

        log_context = LogContext(extra, context_token, self._remove_context)
        return log_context
