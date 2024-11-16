#!/bin/bash


PYTHON_SCRIPT="C:\Users\Michalina\cs4223\Assignment2\CacheCoherenceProtocolsSimulator\Simulator\Main.py"

echo "===blackscholes==="

python $PYTHON_SCRIPT MESI blackscholes 1024 1 16 4
python $PYTHON_SCRIPT Dragon blackscholes 1024 1 16 4

echo "===fluidanimate==="

python $PYTHON_SCRIPT MESI fluidanimate 1024 1 16 4
python $PYTHON_SCRIPT Dragon fluidanimate 1024 1 16 4

echo "===bodytrack==="

python $PYTHON_SCRIPT MESI bodytrack 1024 1 16 4
python $PYTHON_SCRIPT Dragon bodytrack 1024 1 16 4

# For development or testing smaller configurations
# python $PYTHON_SCRIPT MESI test 32 2 8 2
