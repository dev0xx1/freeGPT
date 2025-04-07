import logging
import os


class Logger:

    def __init__(self,
                 name,
                 format='%(levelname)s | %(name)s | %(asctime)s : %(message)s',
                 level=logging.INFO,
                 telegram_channel_id=os.environ.get('TELEGRAM_CHANNEL_ID_LOGS', None)):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False

        handler = logging.StreamHandler()
        formatter = logging.Formatter(format)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.telegram_channel_id = telegram_channel_id
