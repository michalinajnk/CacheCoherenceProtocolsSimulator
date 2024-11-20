import sys
from Simulator.Bus_Logic.Bus import Bus
from Simulator.Cache.CacheController import CacheController
from Simulator.Configuration.Stats import Statistics
from Simulator.Configuration.config import Config
from Simulator.Processor.Processor import Processor
from Simulator.Protocol.DragonProtocol import DragonProtocol
from Simulator.Protocol.MESIProtocol import MESIProtocol
from Simulator.Timer.Timer import Timerr

ROOT_PATH_DATA  = r'C:\Users\Michalina\cs4223\Assignment2\CacheCoherenceProtocolsSimulator\Simulator\Data'
def main(argv):
    assert len(argv) == 7, "Need  to be 7 arguments passed!"
    config = Config(int(argv[6]))
    #set cache config
    config.setCacheConfig(CACHE_SIZE=int(argv[3]),
                        ASSOCIATIVITY= int(argv[4]),
                        BLOCK_SIZE= int(argv[5]))

    config.setTimeConfig(CACHE_HIT=1,LOAD_BLOCK_FR0M_MEM=100, WRITE_BACK_MEM=100, BUS_UPDATE=2)

    # set file name
    filename = argv[2] + "_"  # such as "_0.data"
    directory = argv[2] + "_four"
    print(f"Directory name: {directory}")
    # set coherence protocol
    if argv[1] == "MESI":
        protocol = MESIProtocol(config)
    elif argv[1] == "Dragon":
        protocol = DragonProtocol(config)
    else:
        print("Invalid protocol selected")
        return 1

    config.setProtocl(protocol)

    timer = Timerr()
    bus = Bus(protocol,config )
    timer.set_bus(bus)
    processors = []

    for i in range(config.CPU_NUMS):
        cpu = Processor(i, filename, config, root_path=f"{ROOT_PATH_DATA}/{directory}")
        cpu.cache.set_processor(cpu)
        timer.attach(cpu)
        controller = CacheController(i, bus, cpu.cache)
        cpu.cache.set_controller(controller)
        bus.register_cache(controller)
        config.CPU_STATS.append(Statistics())
        processors.append(cpu)

    config.CPU_STATS.append(Statistics())  # For the bus

    try:
        while True:

            if not timer.tick():  # if any processor returns False, it will stop the timer
                break

            all_finished = True
            for processor in processors:
                if not processor.finished:  # Check each processor's finished status
                    all_finished = False
                    break
            if all_finished:
                print("All processors have completed their tasks.")
                break
        print("\nEnd of simulation at cycle", timer.current_time(), "...")
    except Exception as e:
        logging.error(f"An error occurred during simulation: {str(e)}, {str(e.__traceback__)}, {e.__str__()}")
    except KeyboardInterrupt:
        logging.debug(f"Interrupted by the user")
    finally:
        for i in range(config.CPU_NUMS):
            print(f"=== Statistics about CPU {i} ===")
            print("Finished at cycle", config.CPU_STATS[i].get_count("sum_execution_time"))
            print("Compute Cycles Number is", config.CPU_STATS[i].get_count("compute_cycles"))
            print("Load Number:", config.CPU_STATS[i].get_count("load_number"), "Store Number:", config.CPU_STATS[i].get_count("store_number"))
            idle_cycles = config.CPU_STATS[i].get_count("sum_execution_time") - config.CPU_STATS[i].get_count("compute_cycles")
            print("Idle Cycles Number is", idle_cycles)
            if config.CPU_STATS[i].get_count("store_number") + config.CPU_STATS[i].get_count("load_number") > 0:
                miss_rate = 100 - (config.CPU_STATS[i].get_count("cache_hit") * 100) / (config.CPU_STATS[i].get_count("load_number") + config.CPU_STATS[i].get_count("store_number"))
                print("Data Cache Miss Rate:", f"{miss_rate}%")

        print("=== Statistics about the Bus ===")
        print("Data Traffic:", config.CPU_STATS[config.CPU_NUMS].get_count("data_traffic"), "bytes")
        if config.CPU_STATS[config.CPU_NUMS].get_count("invalidation") != 0:
            print("Number of Invalidations:", config.CPU_STATS[config.CPU_NUMS].get_count("invalidation"))
        else:
            print("Number of Updates:", config.CPU_STATS[config.CPU_NUMS].get_count("update"))

        return 0

if __name__ == "__main__":
    import logging

    # Configure logging
    logging.basicConfig(
        filename='cache_simulation.log',  # Log file path
        filemode='w',  # Overwrite the log file on each run
        level=logging.DEBUG,  # Capture all levels of messages
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Include timestamp
        datefmt='%Y-%m-%d %H:%M:%S'  # Timestamp format
    )

    logging.debug("This is a debug message")
    logging.info("This is an informational message")
    logging.warning("This is a warning message")
    logging.error("This is an error message")
    logging.critical("This is a critical message")
    sys.exit(main(sys.argv))
