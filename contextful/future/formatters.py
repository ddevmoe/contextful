import json
from datetime import datetime
from logging import Formatter, LogRecord, StreamHandler


class JsonFormatter(Formatter):
    """
    Provides funcionality to emit JSON-formatted logs.

    Useful when logging to ndjson files (and to the console if you don't mind the extra clutter).

    Currently in WIP status - does not provide all of it's planned feature set yet, and is not fully tested.
    """

    def __init__(
        self,
        log_record_attribute_mapping: dict[str, str],
        keep_empty_values: bool = False,
        datefmt: str | None = None,
        json_dumps_kwargs: dict | None = None,
        **kwargs,
    ):
        """
        Args:
            log_record_attribute_mapping: mapping of attributes on `LogRecord` instances to their respective keys in the resulting formatted record.
            i.e. to include the level of the log, include a key-value pair in the passed mapping like so:
            `{"levelname": "level"}`

            a common mapping would include the timestamp, level, the message, the context (of a `ContextLogger`, for instance) and exception tracebacks:
            ```
            {
                "asctime": "timestamp",
                "levelname": "level",
                "message": "message",
                "context": "context",
                "exc_text": "traceback",
            }
            ```

            datefmt: log creation timestamp format, isoformat by default (`datetime.isoformat(timespec='seconds')`)
            json_dumps_kwargs: passed unpacked (**json_dumps_kwargs) to the `json.dumps` invocation
    """
        self._log_record_attribute_mapping = log_record_attribute_mapping
        self._keep_empty_values = keep_empty_values
        self._json_dumps_kwargs = json_dumps_kwargs or {}
        super().__init__(datefmt=datefmt, **kwargs)

    def usesTime(self) -> bool:
        return 'asctime' in self._log_record_attribute_mapping

    def formatTime(self, record: LogRecord, datefmt: str | None = None) -> str:
        log_datetime = datetime.fromtimestamp(record.created)

        if datefmt:
            return log_datetime.strftime(datefmt)

        return log_datetime.isoformat(timespec='seconds')

    def _prepare_record(self, record: LogRecord):
        # Maintain behavior of parent Formatter's format method
        record.message = record.getMessage()

        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)

    def format(self, record: LogRecord) -> str:
        self._prepare_record(record)
        record_data = record.__dict__

        formatted_record = {
            key_name: record_data.get(attribute)
            for attribute, key_name in self._log_record_attribute_mapping.items()
            if record_data.get(attribute) or self._keep_empty_values
        }

        stringified_record = json.dumps(formatted_record, default=str, **self._json_dumps_kwargs)
        return stringified_record


if __name__ == '__main__':
    """Usage example"""

    import sys

    from contextful import ContextLogger


    formatter = JsonFormatter({
        'asctime': 'timestamp',
        'levelname': 'level',
        'message': 'message',
        'context': 'context',
        'exc_text': 'traceback',
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
