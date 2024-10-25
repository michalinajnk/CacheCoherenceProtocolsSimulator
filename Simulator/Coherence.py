from Cache import *
from DataParser import *
from Processor import *
from Log import Logger
from Bus import *
import sys
import time

from tqdm import tqdm

DEFAULT_BLOCK_SIZE = 16;
DEFAULT_CACHE_SIZE = 1024;
DEFAULT_ASSOCIATIVITY = 1;

def main():
    t0 = time.time()
    
    if len(sys.argv) == 1:
        print(sys.argv)
        dataset = 'blackscholes'
        # dataset = 'bodytrack'
        # dataset = 'fluidanimate'
        part_id = 0 
        cacheSize = DEFAULT_CACHE_SIZE
        assoc = DEFAULT_ASSOCIATIVITY
        blockSize = DEFAULT_BLOCK_SIZE
    elif len(sys.argv) == 6:
        dataset = sys.argv[1]
        part_id = int(sys.argv[2])
        cacheSize = int(sys.argv[3])
        assoc = int(sys.argv[4])
        blockSize = int(sys.argv[5])
    else:
        print("Invalid number of arguments")
        return

    print('avaliable datasets:', *DATASETS)

    # create dataloader object
    DATALOADER_0 = Dataloader(dataset, part_id)
    # create bus object
    BUS = Bus()
    # create cache object
    CACHE_0 = Cache(cache_size=cacheSize, block_size=blockSize, associativity=assoc, bus=BUS)
    # make a processor object
    PROCESSOR_0 = Processor(CACHE_0, BUS, DATALOADER_0)

    print("===========processor configuration===========")
    PROCESSOR_0.cache.print_config()



    # run the simulation
    cycles = 0
    print("===========simulation started===========")
    while True:
        PROCESSOR_0.nextTick()
        cycles += 1
        # print(cycles)
        if PROCESSOR_0.completed:
            break
        # if cycles % 10000000 == 0:
        #     print(f"Current cycle: {cycles}")
    print(f"Simulation completed in {cycles} cycles")
    print("===========processor status===========")
    PROCESSOR_0.print_stats(totalCycles = cycles)
    print("===========cache status===========")
    PROCESSOR_0.cache.print_stats()
    print("===========bus status===========")
    BUS.print_stats()
    print(f"Time taken: {time.time() - t0:.2f} seconds")

if __name__ == "__main__":
    main()