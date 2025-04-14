# Async Throttle Decorator (Python)

This Python module provides a `throttle` decorator designed to limit the call frequency of asynchronous functions (`async def`). It mimics the behavior of common JavaScript throttle implementations (leading edge trigger, discarding subsequent calls).

## Features

*   **Throttling**: Ensures the decorated async function is called at most once during the specified `wait` period.
*   **Leading Edge Trigger**: The first call within a throttle cycle is executed immediately.
*   **Discarding**: Calls arriving during the cooldown period (within `wait` seconds) are ignored and not queued for later execution.
*   **`asyncio`-based**: Designed specifically for use with Python's `asyncio` library.

## Usage

Apply the `@throttle(wait)` decorator to your async function, where `wait` is the minimum time interval (in seconds) allowed between calls.

```python
# filepath: throttle.py
import asyncio
import time
from throttle import throttle # Assuming the throttle decorator is in this file

@throttle(1.0) # Allow at most one call per second
async def my_throttled_function(arg):
    print(f"{time.monotonic():.2f}: Function called with {arg}")
    await asyncio.sleep(0.2) # Simulate some async work
    print(f"{time.monotonic():.2f}: Function finished")
    return f"Result for {arg}"

async def main():
    # Call the function rapidly
    tasks = [asyncio.create_task(my_throttled_function(i)) for i in range(5)]
    await asyncio.sleep(0.5) # Wait a short period
    tasks.extend([asyncio.create_task(my_throttled_function(i + 5)) for i in range(5)])

    results = await asyncio.gather(*tasks, return_exceptions=True)
    print("\nResults (None indicates a throttled/ignored call):")
    for i, res in enumerate(results):
        print(f"Call {i}: {res}")

if __name__ == "__main__":
    asyncio.run(main())
```

## How to Run the Example

You can run the example usage included in the `throttle.py` file directly:

```bash
python throttle.py
```

You will observe that the function is only called again after the `wait` interval (1.0 second in the example) has passed since the start of the last allowed call. Other calls during the cooldown are ignored (returning `None`).