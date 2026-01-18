import asyncio
import time

async def brew_coffee():
    print("☕️ Starting coffee...")
    await asyncio.sleep(3)  # This "yields" control back to the event loop
    print("☕️ Coffee ready!")

async def toast_bread():
    print("🍞 Starting toast...")
    await asyncio.sleep(2)  # This also yields control
    print("🍞 Toast ready!")

async def main():
    start = time.perf_counter()

    # Run both tasks concurrently
    await asyncio.gather(brew_coffee(), toast_bread())

    end = time.perf_counter()
    print(f"\nTotal time: {end - start:.2f} seconds")

# Run the event loop
asyncio.run(main())
