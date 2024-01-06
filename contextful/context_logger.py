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


_global_context = ContextVar('context_logger_store', default={})


class ContextLogger(logging.Logger):
    def __init__(
        self,
        name: str = 'main',
        level: int | str = logging.NOTSET,
        base_context: dict | None = None,
        top_level_fields: list[str] | None = None,
        always_set_context: bool = False,
    ):
        """
        Args:
            base_context: Context that'll be included in each log (even if no other context is provided).
              Setting `exclude_context` to `True` in underlying logging invocations does NOT exclude the base_context.
            top_level_fields: List of fields that'll be pulled (if found) from given context and placed on the generated `LogRecord` itself.
            always_set_context: Ensure `LogRecord` instances always have a `context` attribute set to an empty `dict`, even when no context is provided.
        """

        self._base_context = (base_context or {}).copy()
        self._top_level_fields = frozenset(top_level_fields or set())
        self._always_set_context = always_set_context
        super().__init__(name, level)

    def _log(self, level: int, msg: object, context: dict | None = None, *args, exclude_context: bool = False, **kwargs):
        if not self.isEnabledFor(level):
            return

        if exclude_context:
            finalized_context = self._base_context.copy()  # `base_context` overpowers `exclude_context`
        else:
            finalized_context = {**self._base_context, **_global_context.get(), **(context or {})}

        extra: dict = kwargs.pop('extra', {})

        if 'context' in extra:
            raise ValueError('Logging "extra" dict must not contain a key named "context" as it is reserved for ContexLogger\'s use')

        # Pop each field in `top_level_fields` found in the given context directly onto `extra` so it'll be set on the generated `LogRecord`
        for field in self._top_level_fields:
            if field in finalized_context:
                extra[field] = finalized_context.pop(field)

        # If there's a context or `always_set_context` is set - assign given context
        if finalized_context or self._always_set_context:
            extra['context'] = finalized_context

        super()._log(level, msg, args, **kwargs, extra=extra)

    def _remove_context(self, log_context: LogContext):
        _global_context.reset(log_context.context_token)

    def context(self, context: dict) -> LogContext:
        current_context = _global_context.get()
        new_context = {**current_context, **context}
        context_token = _global_context.set(new_context)

        log_context = LogContext(context, context_token, self._remove_context)
        return log_context

    #region Log Method Overrides

    def log(self, level: int, msg: object, context: dict | None = None, *args, exclude_context: bool = False, **kwargs):
        self._log(level, msg, context, *args, exclude_context=exclude_context, **kwargs)

    def debug(self, msg: object, context: dict | None = None, *args, exclude_context: bool = False, **kwargs):
        self._log(logging.DEBUG, msg, context, *args, exclude_context=exclude_context, **kwargs)

    def info(self, msg: object, context: dict | None = None, *args, exclude_context: bool = False, **kwargs):
        self._log(logging.INFO, msg, context, *args, exclude_context=exclude_context, **kwargs)

    def warn(self, *args, **kwargs):
        """Warn is unsupported. Use `logger.warning` instead."""
        raise NotImplementedError('Warn is unsupported. Use `logger.warning` instead.')

    def warning(self, msg: object, context: dict | None = None, *args, exclude_context: bool = False, **kwargs):
        self._log(logging.WARNING, msg, context, *args, exclude_context=exclude_context, **kwargs)

    def error(self, msg: object, context: dict | None = None, *args, exclude_context: bool = False, **kwargs):
        self._log(logging.ERROR, msg, context, *args, exclude_context=exclude_context, **kwargs)

    def exception(self, msg: object, context: dict | None = None, *args, exclude_context: bool = False, exc_info: bool = True, **kwargs):
        self._log(logging.ERROR, msg, context, *args, exclude_context=exclude_context, exc_info=exc_info, **kwargs)

    def critical(self, msg: object, context: dict | None = None, *args, exclude_context: bool = False, **kwargs):
        self._log(logging.CRITICAL, msg, context, *args, exclude_context=exclude_context, **kwargs)

    #endregion
