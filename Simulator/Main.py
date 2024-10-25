from Cache import *
from DataParser import *
from Processor import *
from Log import Logger
from Bus import *

from tqdm import tqdm

print('avaliable datasets:', *DATASETS)
dataset = 'blackscholes'
part_id = 0 

# create dataloader object
DATALOADER_0 = Dataloader(dataset, part_id)
# create bus object
BUS = Bus()
# make a processor object
PROCESSOR_0 = Processor(BUS, DATALOADER_0)

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
# 59335497