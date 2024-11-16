@echo off

echo ===blackscholes===
python coherence.py MESI blackscholes 1024 1 16 4
python coherence.py Dragon blackscholes 1024 1 16 4

echo ===fluidanimate===
python coherence.py MESI fluidanimate 1024 1 16 4
python coherence.py Dragon fluidanimate 1024 1 16 4

echo ===bodytrack===
python coherence.py MESI bodytrack 1024 1 16 4
python coherence.py Dragon bodytrack 1024 1 16 4

pause
