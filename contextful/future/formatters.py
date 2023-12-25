import json
import traceback
from datetime import datetime
from logging import Formatter, LogRecord, StreamHandler
from typing import Any


class JsonFormatter(Formatter):
    """
    Provides funcionality to emit JSON-formatted logs.

    Useful when logging to ndjson files (and to the console if you don't mind the extra clutter).

    Currently in WIP status - does not provide all of it's planned feature set yet, and is not fully tested.
    """

    __NO_VALUE_SENTINEL = object()

    def __init__(
        self,
        log_record_attribute_mapping: dict[str, str],
        add_timestamp: bool = True,
        add_traceback: bool = True,
        ensure_ascii: bool = False,
    ):
        """
        log_record_attribute_mapping - mapping of attributes on `LogRecord` instances to their respective keys in the resulting formatted record.
          i.e. to include the level of the log, include a key-value pair in the passed mapping like so:
          `{'levelname': 'level'}`
          a common mapping would include the level, the message and the context (of a `ContextLogger`, for instance):
          `{'levelname': 'level', 'msg': 'message', 'context': 'context}`

        add_timestamp - adds a `timestamp` key to each log using `datetime.now().isoformat(timespec='seconds')`

        add_traceback - adds a `traceback` key to each log if it provides exception information ("exc_info") containing the stringified traceback.

        ensure_ascii - passed directly to a `json.dumps` invocation
        """

        self._log_record_attribute_mapping = log_record_attribute_mapping
        self._add_timestamp = add_timestamp
        self._add_traceback = add_traceback
        self._ensure_ascii = ensure_ascii

    def format(self, record: LogRecord) -> str:
        record_data: dict[str, Any] = {}
        if self._add_timestamp:
            record_data['timestamp'] = datetime.now().isoformat(timespec='seconds')

        for attribute, key_name in self._log_record_attribute_mapping.items():
            value = getattr(record, attribute, self.__NO_VALUE_SENTINEL)
            if value is not self.__NO_VALUE_SENTINEL:
                record_data[key_name] = value

        if self._add_traceback and getattr(record, 'exc_info', None):
            record_data['traceback'] = traceback.format_exc()

        formatted_record = json.dumps(record_data, ensure_ascii=self._ensure_ascii)
        return formatted_record


if __name__ == '__main__':
    """Usage example"""

    import sys

    from contextful import ContextLogger


    formatter = JsonFormatter({
        'levelname': 'level',
        'msg': 'message',
        'context': 'context',
    })
    console_handler = StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger = ContextLogger()
    logger.addHandler(console_handler)

    try:
        x = 10 / 0
    except Exception:
        logger.exception('Was kinda hoping for a miracle there...')

    with logger.context({'name': 'John'}):
        logger.info('Some message from a person', {'last_name': 'Doe'})
        logger.info('Different person', {'name': 'Alex'})
