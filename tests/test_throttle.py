import asyncio
import time
import pytest
from pythrottle import throttle

@throttle(1.0)  # Limit to 1 call per second (at most)
async def my_async_function(name: str):
    print(f"{time.monotonic():.2f}: Function '{name}' called")
    await asyncio.sleep(0.2)  # Simulate some work
    print(f"{time.monotonic():.2f}: Function '{name}' finished")
    return f"Result from {name}"

@pytest.mark.asyncio
async def test_throttle_functionality():
    print("--- Starting JS-like Throttle Test ---")
    # Try calling rapidly
    tasks = []
    start_time = time.monotonic()
    for i in range(9):
        # Stagger calls to demonstrate throttling
        tasks.append(asyncio.create_task(my_async_function(f"Task-{i}")))
        await asyncio.sleep(0.3)  # Call approx every 0.3 seconds

    print(f"{time.monotonic():.2f}: All tasks created.")
    # Wait for tasks to complete (or be ignored)
    results = await asyncio.gather(*tasks, return_exceptions=True)
    print(f"{time.monotonic():.2f}: Gather finished.")
    
    print("--- Results (None indicates ignored call) ---")
    for i, res in enumerate(results):
        print(f"Task-{i}: {res}")
    
    # Basic assertions to verify behavior
    assert results[0] is not None  # First call should execute
    assert None in results  # Some calls should be ignored
    assert any(isinstance(r, str) and r.startswith("Result") for r in results)  # Some calls should return results
