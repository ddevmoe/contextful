# Context Logger

Enhanced logging features emphasizing context for complex logging requirements.

## Installation

Install using pip:

```SHELL
pip install contextful
```

## Usage Example

Here's an example for a process of shipping a couple of items to their respective destinations.

We use logging context to tie each log to it's respective item.

```python
import logging
from context_logger import ContextLogger


class CustomHandler(logging.Handler):
    def emit(record) -> None:
        sender = record.context.get('sender')
        item_id = record.context.get('item_id')
        print(f'[{sender} -> {item_id}] {record.msg}')


logger = ContextLogger()
logger.addHandler(CustomHandler())



def measure_item_weight(item_contents) -> float:
    ...  # Magic here
    logger.info('Item weight was measured successfully')


def determine_item_destination(item) -> str:
    ...  # Magic here
    logger.info('Determined item address')


def ship_item(item):
    ...  # Magic here
    logger.info('Shipped item successfuly')


# Ship some items
sender = 'Johnny John'
items = [Item(id='item-1', ...), Item(id='item-1', ...)]
with logger.context({'sender': sender}):
    for item in items:
        with logger.context({'item': item.id}):
            weight = measure_item_weight(item.contents)
            destination = determine_item_destination(item)
            ship_item(item)

# Output:
# [Johnny John -> item-1] Item weight was measured successfully
# [Johnny John -> item-1] Determined item address
# [Johnny John -> item-1] Shipped item successfuly
# [Johnny John -> item-2] Item weight was measured successfully
# [Johnny John -> item-2] Determined item address
# [Johnny John -> item-2] Shipped item successfuly
```

This simple demonstration showcases two powerful benefits of using a context for logging -

1. We were able to append valuable information - the sender name - to each of the logs on _every item_ without having to propagate down
data that was unnecessary for the logic of the function itself (- we don't need the sender name to measure an item's weight, only the contents).

1. We were able to append an item id to each log without explicitly adding it to any of them, even though
they were invoked in different functions.

## License

This project is open sourced under MIT license, see the [LICENSE](LICENSE) file for more details.
