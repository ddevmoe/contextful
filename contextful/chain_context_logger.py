import inspect
import logging
import uuid
from typing import Callable

from contextlib import AbstractContextManager


class LogContext(AbstractContextManager):
    def __init__(
        self,
        data: dict,
        frame_id: int,
        cleanup_hook: Callable[['LogContext'], None],
        id_: str = None,
    ):
        self.id = id_ or str(uuid.uuid4())
        self.data = data
        self.frame_id = frame_id
        self._cleanup_hook = cleanup_hook

    def __enter__(self, *args, **kwargs):
        return super().__enter__(*args, **kwargs)

    def __exit__(self, *args, **kwargs) -> bool | None:
        self._cleanup_hook(self)
        return super().__exit__(*args, **kwargs)


class FrameContext:
    def __init__(self, frame_id: int, father_frame_context: dict) -> None:
        self._frame_id = frame_id
        self._contexts: list[LogContext] = []
        self._current_context = {}
        self._father_frame_context = father_frame_context

    @property
    def frame_id(self) -> int:
        return self._frame_id

    @property
    def current_context(self) -> dict:
        # father_context = self._father_frame_context.current_context() if self._father_frame_context else {}
        merged_context = {**self._father_frame_context, **self._current_context}
        return merged_context

    @property
    def empty(self) -> bool:
        return not self._contexts

    @staticmethod
    def _merge_contexts(contexts: list[LogContext]) -> dict:
        merged_context = {}
        for context in contexts:
            merged_context.update(context.data)
        
        return merged_context

    def append_context(self, context: LogContext):
        self._contexts.append(context)
        self._current_context = self._merge_contexts(self._contexts)

    def pop_context(self):
        self._contexts.pop()
        self._current_context = self._merge_contexts(self._contexts)


class ContextStore:
    def __init__(self):
        self._store: dict[int, FrameContext] = {}

    def add_context(self, frame_id: int, log_context: LogContext):
        # Invoked on logger.context

        #TODO: If the context is created within an async function, and has no currently existing parent -
        # tie a reference from the latest-common frame (probably one of [run_forever / _run_once / _run])
        # so when a log context is requested (via self.get_context) while still inside the foregin event loop
        # frame chain - the latest NON foreign-chain context is provided
        # That'll create a cross-link between the two (or more!) coexisting frame stacks on the same event loop.

        # If the frame already exists, skip parent frame resolution process
        if frame_id in self._store:
            self._store[frame_id].append_context(log_context)
            return

        parent_frame = inspect.currentframe()
        while parent_frame and id(parent_frame) not in self._store:
            parent_frame = parent_frame.f_back

        if parent_frame is None:
            parent_frame_context = {}
        else:
            parent_frame_context = self._store[id(parent_frame)].current_context
            del parent_frame

        frame_context = FrameContext(frame_id, father_frame_context=parent_frame_context)
        frame_context.append_context(log_context)
        self._store[frame_id] = frame_context

    def pop_context(self, frame_id: int):
        # TODO: BUG?!
        if frame_id not in self._store:
            return

        # TODO: BUG?!
        if not self._store[frame_id]:
            return

        self._store[frame_id].pop_context()
        if self._store[frame_id].empty:
            self._store.pop(frame_id)

    def get_context(self, frame_id: int) -> dict:
        if not self._store:
            return {}

        if frame_id in self._store:
            context = self._store[frame_id].current_context

        parent_frame = inspect.currentframe()
        while parent_frame and id(parent_frame) not in self._store:
            parent_frame = parent_frame.f_back

        if parent_frame is None:
            context = {}
        else:
            context = self._store[id(parent_frame)].current_context
        del parent_frame

        return context


class ContextLogger(logging.Logger):
    def __init__(self, name: str = 'main', level: int = logging.NOTSET):
        super().__init__(name, level)
        self._store = ContextStore()

    def _log(self, level: int, msg: object, *args, extra: dict | None = None, **kwargs) -> None:
        # We hop two frames back (calling_function -> logger.log / logger.info / ... -> logger._log)
        log_frame = inspect.currentframe().f_back.f_back
        log_frame_id = id(log_frame)
        del log_frame

        current_context = self._store.get_context(log_frame_id)
        merged_context = {**current_context, **(extra or {})}
        context_wrapper = {'context': merged_context}
        return super()._log(level, msg, *args, extra=context_wrapper, **kwargs)

    def _remove_context(self, log_context: LogContext):
        self._store.pop_context(log_context.frame_id)

    def context(self, extra: dict) -> LogContext:
        # We hop one frame back (calling_function -> logger.context)
        context_frame = inspect.currentframe().f_back
        context_frame_id = id(context_frame)
        del context_frame

        log_context = LogContext(extra, context_frame_id, cleanup_hook=self._remove_context)

        self._store.add_context(context_frame_id, log_context)

        return log_context
