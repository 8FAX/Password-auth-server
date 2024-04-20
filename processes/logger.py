import logging
from colorama import Fore, Style
import time
from datetime import datetime
import sys
import os
import shutil
from multiprocessing import Process, Queue

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from events.load_config import load_config


def log_parser(log_queue: Queue, config: dict) -> None:
    """
    The `log_parser` function processes logs from a queue, writes them to a log file, and handles server
    shutdown events.

    Author - Liam Scott
    Last update - 04/20/2024
    @param log_queue (any) - The `log_queue` parameter in the `log_parser` function is expected to be a
    queue object that contains log messages to be processed. It is used to retrieve log messages for
    processing within the function.
    @param config (dict) - The `config` parameter is a dictionary containing configuration settings for
    the log parser function. It likely includes information such as the log file path (`log_file`) and
    possibly other settings needed for logging and handling log messages.
    
    """
    timestamp = time.time()

    log_file = config["log_file"]
    logging.basicConfig(filename=log_file, level=logging.DEBUG, filemode="a", format="%(message)s")
    while True:
        log: str = log_queue.get()
        if log == None:
           continue
        if log == "SERVER_SHUTDOWN":
            logging.info(f"Server shutdown - {datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')} - uptime: {(time.time() - timestamp)/60}min")
            logging.shutdown()
            logging.FileHandler(log_file).close()
            archive_logs(log_file, timestamp)
            break
        else:
            logger(log, config)
            
def logger(log: str, config: dict) -> None:
    """
    The function `logger` is designed to handle logging based on specified configurations and log
    messages, allowing logging to terminal, file, or both.
    
    Author - Liam Scott
    Last update - 04/20/2024
    @param log () - The `logger` function takes two parameters: `log` and `config`. The `log` parameter
    seems to be a string containing log information separated by "=", and the `config` parameter is a
    dictionary containing configuration settings for logging.
    @param config () - The `config` parameter in the `logger` function seems to be a dictionary
    containing various configuration settings for logging. Here are the key-value pairs that are being
    used in the function:
    
    """

    log_type: str = config["log_type"]
    log_type = str(log_type)
    log_type = log_type.lower()

    log_value = 0
    log_level: str = config["log_level"]
    log_level = log_level.lower()
    if log_level == "info":
        log_value = 0
    elif log_level == "warning":
        log_value = 1
    elif log_level == "error":
        log_value = 2
    elif log_level == "critical":
        log_value = 3

    log_file: str = config["log_file"]
    debug = config["debug"]
    debug = str(debug)
    debug: str = debug.lower()

    log: list[str] = log.split("=")

    request_debug: str = log[0]
    request_debug = request_debug.lower()

    request_level = log[1]
    request_value = 0

    request_level = request_level.lower()
    if request_level == "info":
        file_request_level: str = "INFO"
        terminal_request_level = f"{Fore.GREEN}INFO"
        request_value = 0

    elif request_level == "warning":
        file_request_level = "WARNING"
        terminal_request_level = f"{Fore.YELLOW}WARNING"
        request_value = 1

    elif request_level == "error":
        file_request_level = "ERROR"
        terminal_request_level = f"{Fore.RED}ERROR"
        request_value = 2
    elif request_level == "critical":
        file_request_level = "CRITICAL"
        terminal_request_level = f"{Fore.RED}CRITICAL"
        request_value = 3

    request_level = request_level.upper()
    request_file = log[2]
    request_message = log[3]
    request_time = log[4]
    request_time = float(request_time)
    request_override = log[5]
    request_override = request_override.lower()

    if log_type == "terminal" or log_type == "both":
        if request_debug == "debug":
            if debug == "true" and request_override == "false":
                if request_value >= log_value:
                    print(f"{Fore.GREEN}DEBUG: {Fore.WHITE}{request_file} {Fore.WHITE}- {terminal_request_level} {Fore.WHITE}- {datetime.fromtimestamp(request_time).strftime('%Y-%m-%d %H:%M:%S')} - {Fore.YELLOW}{request_message}{Style.RESET_ALL}")
            if debug == "false" or request_override == "true":
                pass
        if request_debug == "normal" :
            if request_value >= log_value:
                print(f"{Fore.WHITE}{request_file} {Fore.WHITE}- {terminal_request_level} {Fore.WHITE}- {datetime.fromtimestamp(request_time).strftime('%Y-%m-%d %H:%M:%S')} - {Fore.YELLOW}{request_message}{Style.RESET_ALL}")
        if request_override == "true":
            print(f"{Fore.RED}DEBUG OVERRIDE: {Fore.WHITE}{request_file} {Fore.WHITE}- {terminal_request_level} {Fore.WHITE}- {datetime.fromtimestamp(request_time).strftime('%Y-%m-%d %H:%M:%S')} - {Fore.YELLOW}{request_message}{Style.RESET_ALL}")

    if log_type == "file" or log_type == "both":
        logging.basicConfig(filename=log_file, level=logging.DEBUG, filemode="a", format="%(message)s")
        if request_debug == "debug":
            if debug == "true" and request_override == "false":
                if request_value >= log_value:
                    logging.debug(f"DEBUG: {request_file} - {file_request_level} - {datetime.fromtimestamp(request_time).strftime('%Y-%m-%d %H:%M:%S')} - {request_message}")
            if debug == "false" or request_override == "true":
                pass
        if request_debug == "normal" :
            if request_value >= log_value:
                logging.info(f"{request_file} - {file_request_level} - {datetime.fromtimestamp(request_time).strftime('%Y-%m-%d %H:%M:%S')} - {request_message}")
        if request_override == "true":
            logging.debug(f"DEBUG OVERRIDE: {request_file} - {file_request_level} - {datetime.fromtimestamp(request_time).strftime('%Y-%m-%d %H:%M:%S')} - {request_message}")
    
    if log_type == "none":
        if request_override == "true":
            logging.basicConfig(filename=log_file, level=logging.DEBUG, filemode="a", format="%(message)s")
            print(f"{Fore.RED}DEBUG OVERRIDE: {Fore.WHITE}{request_file} {Fore.WHITE}- {file_request_level} {Fore.WHITE}- {datetime.fromtimestamp(request_time).strftime('%Y-%m-%d %H:%M:%S')} - {Fore.YELLOW}{request_message}{Style.RESET_ALL}")
            logging.debug(f"DEBUG OVERRIDE: {request_file} - {file_request_level} - {datetime.fromtimestamp(request_time).strftime('%Y-%m-%d %H:%M:%S')} - {request_message}")


def archive_logs(log_file: str, start_time: float) -> None:
    """
    The function `archive_logs` archives a log file to a "logs" folder with a timestamped filename if it
    exists, creating the folder if it doesn't.
    
    Author - Liam Scott
    Last update - 04/20/2024
    @param log_file () - The `log_file` parameter in the `archive_logs` function is the path to the log
    file that you want to archive. This function takes the log file and moves it to an "old" file with a
    timestamp in the filename before moving it to a "logs" folder. If the "
    @param start_time () - The `start_time` parameter in the `archive_logs` function is used to specify
    the timestamp from which the log archiving process should start. This timestamp is converted to a
    formatted string (`file_format_time`) to be used in renaming and moving log files.
    
    """
    file_format_time: str = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d_%H-%M-%S')

    if os.path.exists("logs"):
        if os.path.exists(log_file):
            os.rename(log_file, f"{file_format_time}.old")
            shutil.move(f"{file_format_time}.old", "logs")
            print(f"{Fore.GREEN}Log file archived to logs folder{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Log file not found{Style.RESET_ALL}")      
    else:
        print(f"{Fore.RED}Logs folder not found{Style.RESET_ALL}")
        os.mkdir("logs")
        print(f"{Fore.GREEN}Logs folder created{Style.RESET_ALL}")
        if os.path.exists(log_file):
            os.rename(log_file, f"{file_format_time}.old")
            shutil.move(f"{file_format_time}.old", "logs")
            print(f"{Fore.GREEN}Log file archived to logs folder{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Log file not found{Style.RESET_ALL}")

# This is a test function to test the logger
# It will generate logs with different levels, types, files and override options
# It will also test the logger with different log types
# this will not remain in the final version
if __name__ == "__main__":
    
    config = load_config()
    log_queue = Queue()
    logger_process = Process(target=log_parser, args=(log_queue, config))
    logger_process.start()
    print(f"Logger started with PID {logger_process.pid}") 
    msg = ["test log", "this is a major error log", "this is a warning log", "this is a critical log", "this is a normal log", "this is a debug", "this is a debug override", "this is a normal override", "this is a warning override", "this is a error override", "this is a critical override"]
    types = ["info", "warning", "error", "critical"]
    loggers = ["debug", "normal"]
    files = ["logger.py", "main.py", "pusher.py", "logic.py"]
    override = ["false", "true"]
    
    for i in msg :
        for j in types:
            for k in loggers:
                for l in files:
                    for m in override:
                        log_queue.put(f"{k}={j}={l}={i}={time.time()}={m}")
                        time.sleep(0.1)
    log_queue.put("SERVER_SHUTDOWN")


# debug/normal=info/warning/error/critical=name.py=message=time=false/true  