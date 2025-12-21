import time
import cProfile
import pstats
import os
from brs.brs import BRS, Brick, writeBRS, ColorMode

def run_benchmark():
    print("Initializing benchmark...")
    save = BRS()
    
    start_time = time.time()
    print("Creating 500,000 bricks...")
    
    # Pre-allocate if possible (Python lists are dynamic, but we can avoid some overhead)
    # save.bricks = [None] * 500000 
    # Actually, appending is usually fine in Python, but let's just append normally 
    # to simulate typical usage.
    
    for i in range(500000):
        b = Brick()
        b.position = [i % 1000, (i // 1000) % 1000, i // 1000000]
        b.size = [5, 5, 5]
        b.color = ColorMode(0)
        save.bricks.append(b)
        
    save.brickcount = len(save.bricks)
    
    create_duration = time.time() - start_time
    print(f"Brick creation took: {create_duration:.4f} seconds")
    
    output_file = "benchmark_500k.brs"
    
    print(f"Writing to {output_file}...")
    write_start_time = time.time()
    writeBRS(output_file, save)
    write_duration = time.time() - write_start_time
    print(f"Writing took: {write_duration:.4f} seconds")
    
    # Cleanup
    if os.path.exists(output_file):
        os.remove(output_file)

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    run_benchmark()
    profiler.disable()
    
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats(20) # Print top 20 lines
