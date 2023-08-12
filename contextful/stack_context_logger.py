import inspect
import logging
import uuid
from contextlib import AbstractContextManager
from types import FrameType


class LogContext(AbstractContextManager):
    def __init__(self, data: dict, frame_locals: dict, id_: str = None):
        self.id = id_ or str(uuid.uuid4())
        self.data = data
        self._frame_locals = frame_locals

    def __enter__(self):
        self._frame_locals[self.id] = self
        return super().__enter__()

    def __exit__(self, *args, **kwargs) -> bool | None:
        self._frame_locals.pop(self.id, None)
        return super().__exit__(*args, **kwargs)


class ContextLogger(logging.Logger):
    def __init__(self, name: str = 'main', level: int = logging.NOTSET):
        super().__init__(name, level)

    def _get_frame_log_context(self, frame: FrameType) -> LogContext | None:
        log_context = next(
            (
                value
                for value in frame.f_locals.values()
                if isinstance(value, LogContext)
            ),
            None
        )
        return log_context

    def _get_context_data(self) -> dict:
        context_data = {}
        frames = [frame_info.frame for frame_info in inspect.stack()]
        # Reverse the order of frames so the current frame is last
        # Makes merging the contexts more straight forward
        call_ordered_frames = reversed(frames)

        for frame in call_ordered_frames:
            log_context = self._get_frame_log_context(frame)
            if log_context:
                context_data.update(log_context.data)

        return context_data

    def _log(self, level: int, msg: object, *args, extra: dict | None = None, **kwargs) -> None:
        current_context = self._get_context_data()
        merged_context = {**current_context, **(extra or {})}
        context_wrapper = {'context': merged_context}
        return super()._log(level, msg, *args, extra=context_wrapper, **kwargs)

    def __context(self, extra: dict, frame_trace_count: int = 2) -> LogContext:
        frames = [frame_info.frame for frame_info in inspect.stack()]
        caller_frame_locals = frames[frame_trace_count].f_locals
        context = LogContext(extra, caller_frame_locals)
        return context

    def context(self, extra: dict) -> LogContext:
        return self.__context(extra)
