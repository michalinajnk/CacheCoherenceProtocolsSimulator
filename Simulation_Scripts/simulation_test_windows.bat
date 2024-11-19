@echo off
echo ==Setup Directory Results==
if not exist "C:\Users\Michalina\cs4223\Assignment2\CacheCoherenceProtocolsSimulator\Simulation_Result" mkdir "C:\Users\Michalina\cs4223\Assignment2\CacheCoherenceProtocolsSimulator\Simulation_Result"

simulation
echo ===blackscholes===
python "C:\Users\Michalina\cs4223\Assignment2\CacheCoherenceProtocolsSimulator\coherence.py" MESI blackscholes 1024 2 16 4 > "C:\Users\Michalina\cs4223\Assignment2\CacheCoherenceProtocolsSimulator\Simulation_Result\MESI_blackholes_1024_2_16_4.txt"
echo MESI blackscholes complete

python "C:\Users\Michalina\cs4223\Assignment2\CacheCoherenceProtocolsSimulator\coherence.py" Dragon blackscholes 1024 2 16 4 > "C:\Users\Michalina\cs4223\Assignment2\CacheCoherenceProtocolsSimulator\Simulation_Result\Dragon_blackholes_1024_2_16_4.txt"
echo Dragon blackscholes complete

echo ===fluidanimate===
python "C:\Users\Michalina\cs4223\Assignment2\CacheCoherenceProtocolsSimulator\coherence.py" MESI fluidanimate 1024 2 16 4 > "C:\Users\Michalina\cs4223\Assignment2\CacheCoherenceProtocolsSimulator\Simulation_Result\MESI_fluidanimate_1024_2_16_4.txt"
python "C:\Users\Michalina\cs4223\Assignment2\CacheCoherenceProtocolsSimulator\coherence.py" Dragon fluidanimate 1024 2 16 4  > "C:\Users\Michalina\cs4223\Assignment2\CacheCoherenceProtocolsSimulator\Simulation_Result\Dragon_fluidanimate_1024_2_16_4.txt"

echo ===bodytrack===
python "C:\Users\Michalina\cs4223\Assignment2\CacheCoherenceProtocolsSimulator\coherence.py" MESI bodytrack 1024 2 16 4 > "C:\Users\Michalina\cs4223\Assignment2\CacheCoherenceProtocolsSimulator\Simulation_Result\MESI_bodytrack_1024_2_16_4.txt"
python "C:\Users\Michalina\cs4223\Assignment2\CacheCoherenceProtocolsSimulator\coherence.py" Dragon bodytrack 1024 2 16 4 > "C:\Users\Michalina\cs4223\Assignment2\CacheCoherenceProtocolsSimulator\Simulation_Result\Dragon_bodytrack_1024_2_16_4.txt"

echo === All tasks completed, check the Results folder ===
pause
