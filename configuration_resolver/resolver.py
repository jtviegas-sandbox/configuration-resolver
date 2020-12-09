import logging
import os
from typing import Union, Optional, List

from configuration_overrider.abstract_overrider import AbstractOverrider

from configuration_resolver.filesys_configuration import FileSysConfiguration
from configuration_resolver.overriders.dummy.dummy_overrider import DummyOverrider
from configuration_resolver.overriders.environment.environment_overrider import EnvironmentOverrider
from configuration_resolver.overriders.utils_dict import merge_dict, flatten_dict, find_config_entries

log = logging.getLogger(__name__)


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Configuration(metaclass=SingletonMeta):

    @staticmethod
    def init(files: Union[list, str], variables: Optional[dict] = None,
             variable_overriders: List[AbstractOverrider] = None,
             environment_prevalence: bool = True, config_file_filter_keys: List[str] = None):

        overriders = [*variable_overriders] if variable_overriders else []
        if environment_prevalence:
            overriders.append(EnvironmentOverrider())

        return Configuration(files, overriders=overriders, variables=variables,
                             config_file_filter_keys=config_file_filter_keys)

    @staticmethod
    def get_instance():
        return Configuration()


    def __init__(self, files: Union[list, str], variables: Optional[dict] = None,
                 overriders: List[AbstractOverrider] = None, config_file_filter_keys: List[str] = None):
        log.info(f"[__init__|in] ({files},{variables},{overriders}, {config_file_filter_keys})")

        # if not hasattr(Configuration.__instance__, '_Configuration__data'):
        self.__data = self._load(files, variables, overriders or [], config_file_filter_keys or [])

        log.info(f"[__init__|out]")

    def _load(self, files: Union[list, str], variables: Optional[dict],
              overriders: List[AbstractOverrider], config_file_filter_keys: List[str]) -> dict:
        log.info(f"[_load|in] ({files},{variables},{overriders}, {config_file_filter_keys})")

        data = {}
        if variables is not None:
            merge_dict(variables, data)

        FileSysConfiguration(files, data, config_file_filter_keys).read()
        flattened = {}
        flatten_dict(data, flattened)
        data.update(flattened)

        for overrider in overriders:
            for key in data.keys():
                val = overrider.get(key)
                if val is not None:
                    for entry in find_config_entries(key, data):
                        entry_pointer = entry['pointer']
                        entry_key = entry['key']
                        entry_pointer[entry_key] = val

        log.info(f"[_load|out] => {data}")
        return data

    def get(self, key: str):
        log.info(f"[get|in] ({key})")
        result = None
        key_upper = key.upper().replace('.', '_')

        if key_upper not in self.__data.keys():
            raise LookupError(f"key {key} not found")
        result = self.__data[key_upper]
        log.info(f"[get|out] => {result}")
        return result


RESOURCES_DIR = f"{os.path.dirname(os.path.dirname(os.path.realpath(__file__)))}/tests/resources"
JSON_FILE = f"{RESOURCES_DIR}/config_01.json"
JSON_FILES = [f"{RESOURCES_DIR}/config_01.json", f"{RESOURCES_DIR}/config_02.json"]

Configuration.init(JSON_FILES,
                       variables={"dag": {"default": {"retry_delay": 5}}, "server": {"resources": {"cpu": "1xc"}},
                                  "id": 1},
                       config_file_filter_keys=["dev", "prod"],
                       variable_overriders=[DummyOverrider("SERVER_RESOURCES_MEM", 9192),
                                            DummyOverrider("OTHER_VAR8", "STEEL")])
