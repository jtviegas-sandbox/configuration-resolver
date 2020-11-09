import logging

from config_resolver.resolvers.abstract_resolver import AbstractResolver
from config_resolver.resolvers.azure_keyvault.azure_keyvault_reader import AzureKeyVaultReader

log = logging.getLogger(__name__)


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