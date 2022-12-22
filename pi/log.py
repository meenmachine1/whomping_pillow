#!/usr/bin/env python3

import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
import os
import sys

from datetime import datetime
from uuid import uuid4

DT_FMTSTR = "%y-%m-%d_%H-%M"

logger = None

def s_print(s, end="\n"):
    sys.stdout.write(s)
    sys.stdout.write(end)
    sys.stdout.flush()
    
def setUpLogging(log_folder="logs/", log_level=logging.DEBUG, log_to_file=False):
    global logger
    loggerFormat = '%(asctime)s %(levelname)s %(message)s'

    ### Logfile generation ###
    if not(os.path.exists(log_folder) and os.path.isdir(log_folder)):
        try:
            os.mkdir(log_folder)
        except Exception as e:
            sys.stdout.write(f"(ERROR) Log folder `{log_folder}` doesn't exist and can't be made. Got: {str(e)}\n")
            sys.stdout.write("Will only log to stdout.")
            sys.stdout.flush()
            log_folder = ""
            log_to_file = False

    gen_log_name = lambda : f"server_{str(uuid4())[:4]}_{datetime.now().strftime(DT_FMTSTR)}"

    logger = logging.getLogger(__name__)

    log_name = None
    if log_to_file:
        log_name = f"{log_folder}/{gen_log_name()}.log"
        while(os.path.exists(log_name)):
            log_name = f"{log_folder}/{gen_log_name()}.log"

        log_name = os.path.normpath(log_name)

    s_print(f"Logging saving to: {log_name}\n")

    handlers = []
    handlers.append(logging.StreamHandler(sys.stdout))

    if log_name is not None:
        handlers.append(RotatingFileHandler(log_name, maxBytes=(128 * 1024)))
        handlers.append(TimedRotatingFileHandler(log_name, when="W0"))

    logging.basicConfig(format=loggerFormat,
                        handlers=handlers,
                        level=log_level,
                        )

    logger.setLevel(log_level)

def get_logger():
    if not logger:
        setUpLogging()
    return logger