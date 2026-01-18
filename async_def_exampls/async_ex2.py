import asyncio
import random


"""
Summary of the API Patterns
Feature	API Command	Purpose
Start	asyncio.run()	The "Power Button" for your async app.
Group	asyncio.gather()	Run 10 things and wait for all 10 to finish.
Race	asyncio.wait_for()	Give up if a task takes too long.
Background	asyncio.create_task()	"Fire and forget" a task while you do other things.

"""
async def fetch_price(exchange_name):
    print(f"Connecting to {exchange_name}...")
    # Simulate network latency
    latency = random.uniform(0.5, 3.0)
    await asyncio.sleep(latency)

    price = random.randint(90000, 96000)
    print(f"Finished {exchange_name} in {latency:.2f}s")
    return {exchange_name: price}

async def main():
    print("--- Starting Crypto Fetch ---")

    try:
        # We set a strict 2-second timeout for the whole operation
        results = await asyncio.wait_for(
            asyncio.gather(
                fetch_price("Binance"),
                fetch_price("Kraken"),
                fetch_price("Coinbase")
            ),
            timeout=2.0
        )
        print("\nResults:", results)

    except asyncio.TimeoutError:
        print("\n❌ Error: One or more exchanges were too slow!")

if __name__ == "__main__":
    asyncio.run(main())

"""
Group    asyncio.gather()    Run 10 things and wait for all 10 to finish.


what if there is exception in one of the 10 things or if 1 thing is taking too long to finish

This is a critical concern when building production apps like a crypto aggregator. By default, asyncio.gather() is a bit "all or nothing"—if one task fails, it can change how the whole group behaves.

Here is how you handle those two specific scenarios.
1. Handling Exceptions

By default, if one task in gather() raises an exception, the exception is immediately raised to the caller. The other tasks keep running in the background, but you lose the clean list of results.
The Solution: return_exceptions=True

You can tell gather to treat errors just like successful results. Instead of crashing, it will place the Exception object into the resulting list at the correct index.
Python

results = await asyncio.gather(
   fetch_binance(),
   fetch_kraken(), # Imagine this one throws a ConnectionError
   return_exceptions=True
)

for res in results:
   if isinstance(res, Exception):
       print(f"One task failed: {res}")
   else:
       print(f"Task succeeded: {res}")

2. Handling "The Slow Task" (Timeouts)

If 9 tasks take 100ms and 1 task takes 30 seconds, gather() will wait the full 30 seconds. You have two ways to fix this:
Option A: The "Hard" Timeout (Cancel everything)

Wrap the whole gather in wait_for. If the timer hits, everything inside is cancelled.
Python

try:
   # If the group takes > 2 seconds, kill the whole operation
   results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=2.0)
except asyncio.TimeoutError:
   print("The whole group was too slow!")

Option B: The "Individual" Timeout (Best for Aggregators)

Wrap each individual task in a timeout. This way, if Binance is slow, you still get the prices from Kraken and Coinbase.
Python

async def fetch_with_timeout(name):
   try:
       return await asyncio.wait_for(fetch_price(name), timeout=1.0)
   except asyncio.TimeoutError:
       return {name: "Timed Out"}

# Now gather the protected tasks
results = await asyncio.gather(
   fetch_with_timeout("Binance"),
   fetch_with_timeout("Kraken")
)

3. The "New" Professional Way: TaskGroup

If you are using Python 3.11 or newer, the recommended way to handle multiple tasks is using a TaskGroup. It is more robust than gather.

   If one task fails, it automatically cancels the others (avoiding "orphan" tasks).

   It uses a context manager (async with) which makes the code cleaner.

Python

async def main():
   try:
       async with asyncio.TaskGroup() as tg:
           t1 = tg.create_task(fetch_binance())
           t2 = tg.create_task(fetch_kraken())

       # Once the block ends, both are finished
       print(t1.result(), t2.result())

   except ExceptionGroup as eg:
       # TaskGroups raise an ExceptionGroup if one or more tasks fail
       print(f"Caught errors: {eg}")

Summary Table
Scenario	Best Tool	Result
I want all results or nothing	asyncio.gather()	Fast, but fragile.
Don't crash if one fails	gather(..., return_exceptions=True)	You get a list of results + errors.
Stop a slow exchange	asyncio.wait_for()	Prevents hanging connections.
Modern/Safe handling	asyncio.TaskGroup()	Cleanest error management (Python 3.11+).

"""
