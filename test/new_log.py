import logging
import logging.config

logging.config.fileConfig("logging.conf", disable_existing_loggers=False, defaults={'filename': __name__})

def test_log():
    logging.debug('other file - this is debugging')
    logging.critical('other file - this is critical')