import logging

class GetLogger(object):
    def __init__(self, logger_name='django'):
        self.logger_name = logger_name

    def get_logger(self):
        return logging.getLogger(self.logger_name)
