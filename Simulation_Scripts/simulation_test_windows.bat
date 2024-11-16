@echo off

echo ===blackscholes===
python Main.py MESI blackscholes 1024 1 16 4
python Main.py Dragon blackscholes 1024 1 16 4

echo ===fluidanimate===
python Main.py MESI fluidanimate 1024 1 16 4
python Main.py Dragon fluidanimate 1024 1 16 4

echo ===bodytrack===
python Main.py MESI bodytrack 1024 1 16 4
python Main.py Dragon bodytrack 1024 1 16 4

pause
