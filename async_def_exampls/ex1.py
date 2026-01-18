
import time

def brew_coffee():
    print("☕️ Starting coffee...")
    time.sleep(3)  # This "blocks" the entire script
    print("☕️ Coffee ready!")

def toast_bread():
    print("🍞 Starting toast...")
    time.sleep(2)  # This also blocks
    print("🍞 Toast ready!")

start = time.perf_counter()
brew_coffee()
toast_bread()
end = time.perf_counter()

print(f"\nTotal time: {end - start:.2f} seconds")
