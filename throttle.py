import asyncio
import functools
from typing import Callable, Any, Coroutine, Optional, Tuple, Dict, TypeVar

T = TypeVar('T')

def throttle(wait: float):
    """
    Throttle decorator with both leading and trailing edge execution.
    
    All calls will eventually return their results. The first call executes 
    immediately, while subsequent calls during the cooldown are delayed and 
    executed when the cooldown period ends.

    Args:
        wait: The minimum time interval (in seconds) between allowed calls,
              measured from the start of the last allowed call.
    """
    _can_run = True
    _lock = asyncio.Lock()
    _pending_call: Optional[Tuple[Tuple, Dict, asyncio.Future]] = None

    def decorator(func: Callable[..., Coroutine[Any, Any, T]]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            nonlocal _can_run, _pending_call
            
            # Create a Future for this call
            future = asyncio.Future()
            
            async def _execute_func(a, kw, fut):
                try:
                    # Execute function and set result
                    result = await func(*a, **kw)
                    fut.set_result(result)
                except Exception as e:
                    # If exception occurs, set it as Future's exception
                    fut.set_exception(e)
            
            async def _reset_can_run():
                await asyncio.sleep(wait)
                nonlocal _can_run, _pending_call
                # Acquire lock to safely reset flags and handle pending calls
                async with _lock:
                    _can_run = True
                    if _pending_call:
                        # Get pending call
                        args_to_run, kwargs_to_run, fut_to_set = _pending_call
                        _pending_call = None
                        # Set can't run immediately because we need to execute a call
                        _can_run = False

                # Execute pending function call outside the lock
                if not _can_run:
                    # Start a new reset task
                    asyncio.create_task(_reset_can_run())
                    # Execute function
                    await _execute_func(args_to_run, kwargs_to_run, fut_to_set)

            try:
                async with _lock:
                    if not _can_run:
                        # If there's already a pending call, set its result to None
                        if _pending_call:
                            _, _, old_future = _pending_call
                            if not old_future.done():
                                old_future.set_result(None)
                        
                        # Save current call as pending
                        _pending_call = (args, kwargs, future)
                    else:
                        # Allow the call and immediately start cooldown timer
                        _can_run = False
                        # Start reset task in background
                        asyncio.create_task(_reset_can_run())
                        # Execute immediately
                        asyncio.create_task(_execute_func(args, kwargs, future))
                
                # Return future, allowing caller to wait for result
                return await future
                
            except Exception as e:
                if not future.done():
                    future.set_exception(e)
                raise
                
        return wrapper
    return decorator


if __name__ == "__main__":
    import time
    # --- Example Usage ---
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
