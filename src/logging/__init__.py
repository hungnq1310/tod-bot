import logging
import os
import sys 
import time
from torch.distributed import barrier

def init_logger(__name__=None, is_main=True, is_distributed=False, filename=None): 
    if not os.path.exists('./log'): 
        os.mkdir('./log')
    if is_distributed:
        barrier()
    handlers = [logging.StreamHandler(sys.stdout)]
    if filename is not None: 
        handlers.append(logging.FileHandler(filename=filename))
    logging.basicConfig(
        datefmt="%m/%d/%Y %H:%M:%S", 
        level=logging.INFO if is_main else logging.WARN, 
        format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s", 
        handlers=handlers
    )
    logger = logging.getLogger(__name__).setLevel(logging.INFO)
    return logger