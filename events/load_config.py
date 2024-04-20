import json
from multiprocessing import Manager

def load_config():
    """
    The `load_config` function reads a JSON configuration file, extracts specific database configuration
    based on the type, and returns the relevant configuration settings.
    
    Author - Liam Scott
    Last update - 04/19/2024
    @returns The function `load_config` returns a dictionary `shared_config` containing configuration
    settings loaded from a JSON file named 'config.json'. The function processes the configuration data
    by extracting values based on the database type specified in the configuration and then removes
    unnecessary configuration settings based on the database type. The final `shared_config` dictionary
    is returned after processing.
    
    """
    with open('config.json', 'r') as f:
        config = json.load(f)

    manager = Manager()
    shared_config = manager.dict()

    for key, value in config.items():
        for sub_key, sub_value in value.items():
            shared_config[sub_key] = sub_value
           #print(f"{key} - {sub_key}: {sub_value}")

    database_type = shared_config["type"]
    if database_type == "sqlite":
        shared_config.pop("mysql_config", None)
        shared_config.pop("postgres_config", None)

    elif database_type == "mysql":
        shared_config.pop("sqlite_config", None)
        shared_config.pop("postgres_config", None)
    
    elif database_type == "postgres":
        shared_config.pop("mysql_config", None)
        shared_config.pop("sqlite_config", None)

    log_type = shared_config["log_type"]
    if log_type == "terminal":
        shared_config.pop("file_path", None)
        
        
    return shared_config

# The `if __name__ == "__main__":` block in Python is used to ensure that the code inside it is only
# executed when the script is run directly, and not when it is imported as a module in another script.
if __name__ == "__main__":

    test = load_config()
    print ("==== TEST ====\n",test,"\n==== TEST ====")
    
