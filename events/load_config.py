import json
from multiprocessing import Manager

def load_config():
    with open('config.json', 'r') as f:
        config = json.load(f)

    manager = Manager()
    shared_config = manager.dict(config)

    return shared_config