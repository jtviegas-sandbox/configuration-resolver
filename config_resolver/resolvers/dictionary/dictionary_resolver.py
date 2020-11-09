import logging

from config_resolver.resolvers.abstract_resolver import AbstractResolver
from config_resolver.resolvers.azure_keyvault.azure_keyvault_reader import AzureKeyVaultReader

log = logging.getLogger(__name__)


class DictResolver(AbstractResolver):

    def __init__(self, config: dict):
        log.info(f"[__init__|in] ({config}")


        self.reader = AzureKeyVaultReader(config['tenant_id'], config['client_id'], config['client_secret'],
                                          config['vault_url'])
        log.info(f"[__init__|out]")

    def __process_dict(self, source: str, prefix: str):
        log.info(f"[process_dict|in] ({source},{prefix})")

        for k in source.keys():
            value = source[k]
            input_type = type(value).__name__
            var_name = f"{'' if prefix is None else prefix.upper() + '_'}{k.upper()}"
            if input_type == 'dict':
                self.__process_dict(value, var_name)

            log.info(f"[process_dict] adding new config {var_name}: {value}")
            self.__data[var_name] = value

        log.info(f"[process_dict|out]")

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

