import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler


class ParserLogger:
    """
    Логирование событий парсера
    """
    def __init__(self):
        self.timestamp_suffix = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        logging.basicConfig(handlers=[self.get_stream_handler(loggin_level='INFO'),
                                      self.get_file_handler(pathfile=f"/log_{self.timestamp_suffix}.txt",
                                                            log_dir='../logs',
                                                            loggin_level='INFO',
                                                            rotate_size="1M",
                                                            rotate_count=5)],
                            format='%(asctime)s|%(levelname)s|%(name)s|%(filename)s|%(lineno)s|%(message)s',
                            datefmt='%d-%m-%Y %H:%M:%S',
                            level='INFO')

    def get_stream_handler(self, loggin_level):
        """ Хендлер терминала """
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setLevel(level=loggin_level)
        return stream_handler

    def get_file_handler(self, pathfile: str, loggin_level, log_dir=None, rotate_size=None,
                         rotate_count=None):
        """ Файл """
        self.check_path(log_dir)
        file_handler = RotatingFileHandler(filename="{0}/{1}".format(log_dir, pathfile),
                                           maxBytes=int(''.join(filter(lambda i: i.isdigit(), rotate_size)))
                                                    * 1024 * 1024,
                                           backupCount=rotate_count,
                                           encoding='utf-8')
        file_handler.setLevel(level=loggin_level)
        return file_handler

    @staticmethod
    def check_path(directory):
        if not os.path.isdir(directory):
            os.makedirs(directory)
