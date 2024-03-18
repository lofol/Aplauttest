import os
import json


class ConfigFileError(Exception):
    pass


class Cfg:
    """ Работает с файлом конфигурации в формате JSON"""

    def __init__(self, file='config.json'):
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), file)
        if os.path.isfile(file_path):
            self.filepath = file_path
        else:
            raise ConfigFileError(f'{file_path} отсутствует либо не является файлом!')

    def load(self):
        """ Загружает файл конфигурации """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigFileError(f'{self.filepath} не является json-файлом!')
