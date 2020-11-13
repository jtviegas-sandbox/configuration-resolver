import logging

from config_resolver.overriders.abstract_overrider import AbstractOverrider
from config_resolver.overriders.azure_keyvault.azure_keyvault_reader import AzureKeyVaultReader

log = logging.getLogger(__name__)


class AzureKeyVaultOverrider(AbstractOverrider):

    def __init__(self, config: dict):
        log.info(f"[__init__|in] ({[k + ':' + v[0:3] for k, v in config.items()]}")
        AbstractOverrider.validate_configuration(['tenant_id', 'client_id', 'vault_url', 'client_secret'], config)
        self.reader = AzureKeyVaultReader(config['tenant_id'], config['client_id'], config['client_secret'],
                                          config['vault_url'])
        log.info(f"[__init__|out]")

    def get(self, key) -> str:
        log.info(f"[get|in] ({key})")
        result = None
        key_upper = key.upper().replace('_', '-')
        try:
            result = self.reader.get_secret(key_upper)
        except Exception as x:
            log.debug(f"secret not found: {key_upper}", exc_info=x)
        log.info(f"[get|out] => {result[0:3] if result is not None else 'None'}")
        return result
