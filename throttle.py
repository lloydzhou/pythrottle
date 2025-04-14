import asyncio
import functools
import time
from typing import Callable, Any, Coroutine, Optional

def throttle(wait: float):
    """
    Throttle decorator mimicking common JavaScript behavior (leading edge, discard).

    Ensures that the decorated async function is called at most once during
    the specified `wait` period. Calls arriving during the cooldown are ignored.
    The first call in a cycle is executed immediately (leading edge).

    Args:
        wait: The minimum time interval (in seconds) between allowed calls,
              measured from the start of the last allowed call.
    """
    _can_run = True
    _lock = asyncio.Lock()

    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Optional[Any]:
            nonlocal _can_run
            try:
                if _lock.locked():
                    return None # Another call is processing or resetting

                # --- Schedule resetting the flag immediately ---
                async def _reset_can_run():
                    await asyncio.sleep(wait)
                    nonlocal _can_run
                    # Acquire lock to safely reset the flag
                    async with _lock:
                        _can_run = True

                async with _lock:
                    if not _can_run:
                        return None # Throttled, ignore this call

                    # Allow the call and immediately start the cooldown timer
                    _can_run = False
                    # Start the reset task in the background
                    asyncio.create_task(_reset_can_run())

                # --- Execute the function outside the lock ---
                # The cooldown timer (_reset_can_run) is already running concurrently.
                result = await func(*args, **kwargs)
                # asyncio.create_task(_reset_can_run())
                return result # Return the result of the allowed call

            except Exception as e:
                 # If an error occurs *after* the reset task was created,
                 # the reset task will still run and eventually allow future calls.
                 # This is generally the desired behavior for throttling.
                 raise # Re-raise the exception
            finally:
                # No specific cleanup needed here in this revised logic.
                pass

        return wrapper
    return decorator


if __name__ == "__main__":
    # --- 示例用法 ---
    @throttle(1.0) # Limit to 1 call per second (at most)
    async def my_async_function(name: str):
        print(f"{time.monotonic():.2f}: Function '{name}' called")
        await asyncio.sleep(0.2) # Simulate some work
        print(f"{time.monotonic():.2f}: Function '{name}' finished")
        return f"Result from {name}"

    async def main():
        print("--- Starting JS-like Throttle Test ---")
        # Try calling rapidly
        tasks = []
        start_time = time.monotonic()
        for i in range(9):
            # Stagger calls to demonstrate throttling
            tasks.append(asyncio.create_task(my_async_function(f"Task-{i}")))
            await asyncio.sleep(0.3) # Call approx every 0.3 seconds

        print(f"{time.monotonic():.2f}: All tasks created.")
        # Wait for tasks to complete (or be ignored)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        print(f"{time.monotonic():.2f}: Gather finished.")
        print("--- Results (None indicates ignored call) ---")
        for i, res in enumerate(results):
            print(f"Task-{i}: {res}")
        print("--- Test End ---")

    asyncio.run(main())
