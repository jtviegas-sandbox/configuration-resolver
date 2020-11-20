import logging
from typing import Union, Optional, List

from configuration_overrider.abstract_overrider import AbstractOverrider

from configuration_resolver.filesys_configuration import FileSysConfiguration
from configuration_resolver.overriders.environment.environment_overrider import EnvironmentOverrider
from configuration_resolver.overriders.utils_dict import merge_dict, flatten_dict, find_config_entries

log = logging.getLogger(__name__)


class Singleton:
    def __new__(cls, *args, **kwargs):
        instance = cls.__dict__.get("__instance__", None)
        if instance is None:
            instance = cls.__instance__ = object.__new__(cls)
            for key, value in kwargs.items():
                setattr(instance, f"_{key}", value)
        return instance


class Configuration(Singleton):

    @staticmethod
    def get_instance(files: Union[list, str], variables: Optional[dict] = None,
                     variable_overriders: List[AbstractOverrider] = [],
                     environment_prevalence: bool = True, config_file_filter_keys: List[str] = []):

        overriders = [*variable_overriders]
        if environment_prevalence:
            overriders.append(EnvironmentOverrider())

        return Configuration(files, overriders=overriders, variables=variables,
                             config_file_filter_keys=config_file_filter_keys)

    def __init__(self, files: Union[list, str], variables: Optional[dict] = None,
                 overriders: List[AbstractOverrider] = [],
                 config_file_filter_keys: List[str] = []):
        log.info(f"[__init__|in] ({files},{variables},{overriders}, {config_file_filter_keys})")

        self.__data = {}
        if variables is not None:
            merge_dict(variables, self.__data)

        self.__data.update(FileSysConfiguration(files, self.__data, config_file_filter_keys).read())
        flattened = {}
        flatten_dict(self.__data, flattened)
        self.__data.update(flattened)

        for overrider in overriders:
            for key in self.__data.keys():
                val = overrider.get(key)
                if val is not None:
                    for entry in find_config_entries(key, self.__data):
                        entry_pointer = entry['pointer']
                        entry_key = entry['key']
                        entry_pointer[entry_key] = val

        log.info(f"[__init__|out]")

    def get(self, key: str):
        log.info(f"[get|in] ({key})")
        result = None
        key_upper = key.upper().replace('.', '_')

        if key_upper not in self.__data.keys():
            raise LookupError(f"key {key} not found")
        result = self.__data[key_upper]
        log.info(f"[get|out] => {result}")
        return result


