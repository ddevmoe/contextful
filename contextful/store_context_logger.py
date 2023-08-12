import logging
import uuid
from contextlib import AbstractContextManager
from typing import Callable


class LogContext(AbstractContextManager):
    def __init__(
        self,
        data: dict,
        setup_hook: Callable[['LogContext'], None],
        cleanup_hook: Callable[['LogContext'], None],
        id_: str = None,
    ):
        self.id = id_ or str(uuid.uuid4())
        self.data = data
        self._setup_hook = setup_hook
        self._cleanup_hook = cleanup_hook

    def __enter__(self, *args, **kwargs):
        self._setup_hook(self)
        return super().__enter__(*args, **kwargs)

    def __exit__(self, *args, **kwargs) -> bool | None:
        self._cleanup_hook(self)
        return super().__exit__(*args, **kwargs)


class ContextStore:
    def __init__(self):
        self._context_store: list[LogContext] = [] 
        self._current_context: dict = {}

    @property
    def current_context(self) -> dict:
        return self._current_context

    def append_context(self, log_context: LogContext):
        # On context enter
        self._context_store.append(log_context)
        updated_context = {**self._current_context, **log_context.data}
        self._current_context = updated_context

    def pop_context(self):
        # On context exit
        self._context_store.pop()

        updated_context = {}
        for context in self._context_store:
            updated_context.update(context.data)

        self._current_context = updated_context


class ContextLogger(logging.Logger):
    def __init__(self, name: str = 'main', level: int = logging.NOTSET):
        super().__init__(name, level)
        self._context_store = ContextStore()

    def _create_log_context_hook(self, log_context: LogContext):
        self._context_store.append_context(log_context)

    def _remove_log_context_hook(self, _log_context: LogContext):
        self._context_store.pop_context()

    def _log(self, level: int, msg: object, *args, extra: dict | None = None, **kwargs) -> None:
        current_context = self._context_store.current_context
        merged_context = {**current_context, **(extra or {})}
        context_wrapper = {'context': merged_context}
        return super()._log(level, msg, *args, extra=context_wrapper, **kwargs)

    def context(self, extra: dict) -> LogContext:
        context = LogContext(
            extra,
            setup_hook=self._create_log_context_hook,
            cleanup_hook=self._remove_log_context_hook,
        )
        return context
