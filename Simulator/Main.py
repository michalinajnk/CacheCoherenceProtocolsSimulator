from Cache import *
from DataParser import *
from Processor import *
from Log import Logger

from tqdm import tqdm

print('avaliable datasets:', *DATASETS) 


# make a processor object
PROCESSOR_0 = Processor()

# read the trace data
dataset = 'blackscholes'
part_id = 0
trace_data = load_trace_file(dataset, part_id, max_trace=-1)



print('Processing trace data...')
for label, value in trace_data:
    # print(label, value)
    PROCESSOR_0.parse_instruction(label, value)

    
print('total clock cycles:', PROCESSOR_0.get_clock())
    