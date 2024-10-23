import os
from tqdm import tqdm

DATASETS = ['blackscholes', 'bodytrack','fluidanimate']

def load_trace_file(dataset_name : str, part_id : int, max_trace = -1):
    """
    Load trace data from a specified file.
    Args:
        dataset_name (str): The name of the dataset.
        part_id (int): The part identifier of the dataset.
        max_trace (int, optional): The maximum number of traces to load. Defaults to -1, which means all traces will be loaded.
    Returns:
        list: A list of tuples where each tuple contains an integer label and a string value representing a trace entry.
    Raises:
        FileNotFoundError: If the specified file does not exist.
    Example:
        >>> load_trace_file('dataset', 1, 100)
        loading dataset_four/dataset_1.data...
        dataset_1.data : 100 trace(s) loaded
        [(1, 'value1'), (2, 'value2'), ...]
    """
    file_path = f'{dataset_name}_four/{dataset_name}_{part_id}.data'
    trace = []
    print(f'loading {file_path}...')
    if not os.path.exists(file_path):
        print(f'{file_path} not found')
        return trace
    with open(file_path, 'r') as file:
        counter = 0
        for line in tqdm(file):
            if counter >= max_trace and max_trace != -1:
                break
            label, value = line.split()
            trace.append((int(label), str(value)))  
            counter += 1
    print(f'{dataset_name}_{part_id}.data : {len(trace)} trace(s) loaded')
    return trace

class Dataloader:
    def __init__(self, dataset, part_id):
        self.trace_data = load_trace_file(dataset, part_id, max_trace=-1)
        self.current_trace = 0
    
    def getInstruction(self):
        if self.current_trace < len(self.trace_data):
            self.current_trace += 1
            return self.trace_data[self.current_trace - 1]
        # end of trace
        return None
                

