import json
import logging
from typing import Union, Optional, List

from config_resolver.filesys_configuration import FileSysConfiguration
from config_resolver.overriders.abstract_overrider import AbstractOverrider
from config_resolver.overriders.azure_keyvault.azure_keyvault_overrider import AzureKeyVaultOverrider
from config_resolver.overriders.databricks_keyvault.databricks_keyvault_overrider import SparkKeyVaultOverrider
from config_resolver.overriders.environment.environment_overrider import EnvironmentOverrider
from config_resolver.overriders.utils_dict import merge_dict, flatten_dict, merge_flattened, find_config_entries

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
                     spark_keyvault_config: Optional[dict] = None, azure_keyvault_config: Optional[dict] = None,
                     variable_overriders: List[AbstractOverrider] = [],
                     environment_prevalence: bool = True, merge_flatenned_variables: bool = True,
                     config_file_filter_keys: List[str] = []):

        if azure_keyvault_config is not None:
            variable_overriders.append(AzureKeyVaultOverrider(azure_keyvault_config))

        if spark_keyvault_config:
            variable_overriders.append(SparkKeyVaultOverrider(spark_keyvault_config))

        overriders = [*variable_overriders]
        if environment_prevalence:
            overriders.append(EnvironmentOverrider())

        return Configuration(files, overriders=overriders, variables=variables,
                             merge_flatenned=merge_flatenned_variables, config_file_filter_keys=config_file_filter_keys)

    def __init__(self, files: Union[list, str], variables: Optional[dict] = None,
                 overriders: List[AbstractOverrider] = [], merge_flatenned: bool = True,
                 config_file_filter_keys: List[str] = []):
        log.info(f"[__init__|in] ({files},{variables},{overriders},{merge_flatenned}, {config_file_filter_keys})")

        self.__data = {}
        if variables is not None:
            """why merge? because that's the way of adding and we are well behaved"""
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

#                    if merge_flatenned:
#                        merge_flattened({key: val}, self.__data)

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


