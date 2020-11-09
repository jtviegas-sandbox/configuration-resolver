import logging
from typing import Union, Optional

from config_resolver.filesys_configuration import FileSysConfiguration
from config_resolver.resolvers.azure_keyvault.azure_keyvault_resolver import AzureKeyVaultResolver
from config_resolver.resolvers.environment.environment_resolver import EnvironmentResolver
from config_resolver.resolvers.utils_dict import merge_dict, flatten_dict

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
    def get_instance(filesys_input: Union[list, str],
                az_keyvault_config: Optional[dict] = None, env_vars=True, base_vars: Optional[dict] = None):
        additional_resolvers = []
        if az_keyvault_config is not None:
            additional_resolvers.append(AzureKeyVaultResolver(az_keyvault_config))
        if env_vars:
            additional_resolvers.append(EnvironmentResolver())

        return Configuration(filesys_input, additional_resolvers=additional_resolvers, base_vars=base_vars)

    def __init__(self, filesys_input: Union[list, str], additional_resolvers: list = [],
                 base_vars: Optional[dict] = None):
        log.info(f"[__init__|in] ({filesys_input},{additional_resolvers},{base_vars})")

        self.__input = {'filesys_input': filesys_input}
        self.__data = {}
        if base_vars is not None:
            merge_dict(base_vars, self.__data)

        self.__data.update(FileSysConfiguration(filesys_input, self.__data).read())
        flattened = {}
        flatten_dict(self.__data, flattened)
        self.__data.update(flattened)

        for resolver in additional_resolvers:
            for key in self.__data.keys():
                _val = resolver.get(key)
                if _val is not None:
                    self.__data[key] = _val

        log.info(f"[__init__|out]")

    def get(self, key: str):
        log.info(f"[get|in] ({key})")
        _result = None
        _key = key.upper().replace('.', '_')

        if _key not in self.__data.keys():
            raise LookupError(f"key {key} not found")
        _result = self.__data[_key]
        log.info(f"[get|out] => {_result}")
        return _result


