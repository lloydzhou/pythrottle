# PyThrottle

PyThrottle is a Python library that provides an asynchronous throttling decorator inspired by JavaScript throttle patterns.

## Features

- **Async-first**: Designed specifically for throttling asynchronous function calls
- **Leading Edge Execution**: The first call in a cycle executes immediately
- **Trailing Edge Execution**: The most recent call during cooldown is executed when the cooldown period ends
- **Result Preservation**: All calls return their execution results (either immediately or after delay)
- **Simple API**: Clean and easy-to-use decorator syntax


## Usage

### Basic Example

```python
import asyncio
from throttle import throttle

@throttle(1.0)  # Throttle to one call per second
async def fetch_data(query: str):
    # Simulating API call or resource-intensive operation
    await asyncio.sleep(0.2)
    return f"Results for {query}"

async def main():
    # Rapid calls will be throttled
    tasks = []
    for i in range(5):
        tasks.append(asyncio.create_task(fetch_data(f"query-{i}")))
        await asyncio.sleep(0.3)  # Try calling every 0.3 seconds
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)
    
    # Only some calls will return actual results
    # (first call and the most recent call during each cooldown period)
    print(results)

asyncio.run(main())
```

## How It Works

1. When a throttled function is called for the first time, it executes immediately
2. A cooldown period starts, during which new calls are not executed immediately
3. During the cooldown, only the most recent call is saved
4. When the cooldown period ends, if there is a saved call, it is executed and a new cooldown begins
5. All calls return Futures that eventually resolve to either their result or None

## Use Cases

- Rate limiting API requests
- Preventing UI element updates from happening too frequently
- Controlling frequency of resource-intensive operations
- Managing event handler firing rates (e.g., scroll, resize, etc.)

## License

[MIT License](LICENSE)