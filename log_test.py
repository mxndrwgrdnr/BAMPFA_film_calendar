import logging
import requests
logging.basicConfig(filename='test.log',level=logging.INFO, format='%(message)s')
logging.getLogger('requests').setLevel(logging.WARNING)
logging.info('test')
