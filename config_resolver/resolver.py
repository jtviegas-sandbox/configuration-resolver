import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Union, Optional

from config_resolver.azure_keyvault_reader import AzureKeyVaultReader

log = logging.getLogger(__name__)


class AbstractResolver(ABC):

    def _validate_configuration(self, keys: list, config: dict):
        log.info(f"[_validate_configuration|in] (keys:{keys} config:{[k + ':' + v[0:3] for k, v in config.items()]})")
        if not set(keys).issubset(set(config.keys())):
            raise ValueError(f"mandatory config keys not provided: {keys} not a subset of {config.keys()}")
        log.info(f"[_validate_configuration|out]")

    @abstractmethod
    def get(self, key) -> str:
        pass


class EnvironmentResolver(AbstractResolver):

    def get(self, key) -> str:
        log.info(f"[get|in] ({key})")
        _result = None
        try:
            _result = os.environ[key]
        except KeyError as x:
            log.debug(f"environment variable not found: {key}", exc_info=x)

        log.info(f"[get|out] => {_result if _result is not None else 'None'}")
        return _result


class AzureKeyVaultResolver(AbstractResolver):

    def __init__(self, config: dict):
        log.info(f"[__init__|in] ({[k + ':' + v[0:3] for k, v in config.items()]}")
        super()._validate_configuration(['tenant_id', 'client_id', 'vault_url', 'client_secret'], config)
        self.reader = AzureKeyVaultReader(config['tenant_id'], config['client_id'], config['client_secret'],
                                          config['vault_url'])
        log.info(f"[__init__|out]")

    def get(self, key) -> str:
        log.info(f"[get|in] ({key})")
        _result = None
        _key = key.upper().replace('_', '-')
        try:
            _result = self.reader.get_secret(_key)
        except Exception as x:
            log.debug(f"secret not found: {_key}", exc_info=x)
        log.info(f"[get|out] => {_result[0:3] if _result is not None else 'None'}")
        return _result


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
    def factory(filesys_input: Union[list, str], variable_prefix: str = None,
                az_keyvault_config: Optional[dict] = None, env_vars=True):
        additional_resolvers = []
        if az_keyvault_config is not None:
            additional_resolvers.append(AzureKeyVaultResolver(az_keyvault_config))
        if env_vars:
            additional_resolvers.append(EnvironmentResolver())

        return Configuration(filesys_input, additional_resolvers=additional_resolvers)

    def __init__(self, filesys_input: Union[list, str], variable_prefix: str = None,
                 additional_resolvers: list = [], ):
        log.info(f"[__init__|in] ({filesys_input},{variable_prefix},{additional_resolvers})")

        self.__var_prefix = variable_prefix
        self.__input = {'filesys_input': filesys_input}
        self.__data = {}

        self.__data.update(FileSysHandler().resolve(filesys_input, variable_prefix))

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


class FileSysHandler:

    def __process_file(self, source: str, prefix: str):
        log.info(f"[process_file|in] ({source},{prefix})")

        with open(source) as json_file:
            # json content is in itself a dict
            self.__process_dict(json.load(json_file), prefix)

        log.info(f"[process_file|out]")

    def __process_dict(self, source: str, prefix: str):
        log.info(f"[process_dict|in] ({source},{prefix})")

        for k in source.keys():
            _value = source[k]
            _type = type(_value).__name__
            _prefix = f"{'' if prefix is None else prefix.upper() + '_'}{k.upper()}"
            if _type == 'dict':
                self.__process_dict(_value, _prefix)

            log.info(f"[process_dict] adding new config {_prefix}: {_value}")
            self.__data[_prefix] = _value

        log.info(f"[process_dict|out]")

    def __handle_array(self, source: list, prefix: str):
        log.info(f"[handle_array|in] ({source},{prefix})")

        for _f in source:
            if os.path.isdir(_f):
                self.__handle_dir(_f, prefix)
            elif os.path.isfile(_f):
                self.__handle_file(_f, prefix)
            else:
                raise ValueError(f"{_f} is neither a file nor a folder")

        log.info(f"[handle_array|out]")

    def __handle_file(self, source: str, prefix: str):
        log.info(f"[handle_file|in] ({source},{prefix})")

        if source.endswith(".json") or source.endswith(".JSON"):
            self.__process_file(source, prefix)
        else:
            raise ValueError(f"{source} is not a json file")

        log.info(f"[handle_file|out]")

    def __handle_dir(self, source: str, prefix: str):
        log.info(f"[handle_dir|in] ({source},{prefix})")

        for _f in os.listdir(source):
            _entry = os.path.join(source, _f)
            if os.path.isdir(_entry):
                self.__handle_dir(_entry, prefix)
            elif os.path.isfile(_entry):
                self.__handle_file(_entry, prefix)
            else:
                raise ValueError(f"{_entry} is neither a file nor a folder")

        log.info(f"[handle_dir|out]")

    def __init__(self):
        self.__data = {}

    def resolve(self, fs_refs: Union[list, str], var_prefix: str):
        log.info(f"[__init__|in] ({fs_refs},{var_prefix})")
        self.__data = {}

        _type = type(fs_refs).__name__
        if _type == 'str':
            if os.path.isdir(fs_refs):
                self.__handle_dir(fs_refs, var_prefix)
            elif os.path.isfile(fs_refs):
                self.__handle_file(fs_refs, var_prefix)
            else:
                raise ValueError(f"{fs_refs} is neither a file nor a folder")
        elif _type == 'list':
            self.__handle_array(fs_refs, var_prefix)
        else:
            raise TypeError(f"{fs_refs} is neither a list nor a string")

        log.info(f"[__init__|out] => {self.__data}")
        return self.__data
