import logging
import logging.config
from new_log import test_log


logging.config.fileConfig("logging.conf")
logger = logging.getLogger(__name__)
logger.info('test info logging')
logger.info
import sys
sys.exit()

fmt = '%(asctime)s: %(name)s: %(threadName)s: %(levelname)s: %(message)s'
formatter = logging.Formatter(fmt, datefmt='%Y-%m-%d %H:%M:%S')

handler = logging.FileHandler('test.log')
handler.setFormatter(formatter)

handler2 = logging.FileHandler('worse.log')
handler2.setLevel(logging.WARNING)
handler2.setFormatter(formatter)

logger = logging.Logger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.addHandler(handler2)

logger.info('it worked')
logger.warning('rip not worked (warning)')


logging.basicConfig(level=logging.DEBUG, format=fmt, datefmt='%Y-%m-%d %H:%M:%S')


logging.debug('this is debugging')
logging.info('this is infoing')
logging.warning('this is a warning')

test_log()