#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import logging
from helpers import create_storage


# logging
log_level   = logging.INFO  # log level: logging.DEBUG | logging.INFO | logging.WARNING | logging.ERROR
#log_level   = logging.DEBUG
LOGS_FOLDER = "logs"        # log folder


def setup_logger(logger_name, level=log_level, msgformat='%(message)s'):
    l = logging.getLogger(logger_name)

    logging.addLevelName(logging.DEBUG,   "DBG")
    logging.addLevelName(logging.INFO,    "NFO")
    logging.addLevelName(logging.WARNING, "WRN")
    logging.addLevelName(logging.ERROR,   "ERR")

    logfile = logging.FileHandler(os.path.join(LOGS_FOLDER, logger_name + ".log"), mode='w', encoding="UTF-8")
    formatter = logging.Formatter(msgformat)
    logfile.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(logfile)

    return l


# setup loggers
create_storage(LOGS_FOLDER)
logging.basicConfig(level=log_level)
log             = setup_logger('main', msgformat='%(levelname)s: %(message)s')
log_non_english = setup_logger('log_non_english')
log_unsupported = setup_logger('log_unsupported')
log_no_words    = setup_logger('log_no_words')
log_uncatched_template = setup_logger('log_uncatched_template')
log_lang_section_not_found = setup_logger('log_lang_section_not_found')
log_tos_section_not_found = setup_logger('log_tos_section_not_found')
log_wikidata = setup_logger('log_wikidata')
