import logging
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient

log = logging.getLogger(__name__)


class AzureKeyVaultReader:

    def __init__(self, tenant_id: str, client_id: str, client_secret: str, vault_url: str):
        log.info(f"[__init__|in] ({tenant_id},{client_id}, {client_secret[0:3]}..., {vault_url})")
        self.client = SecretClient(vault_url=vault_url,
                                   credential=ClientSecretCredential(tenant_id, client_id, client_secret))
        log.info(f"[__init__|out]")

    def get_secret(self, key: str):
        log.info(f"[get_secret|in] ({key})")
        _result = self.client.get_secret(key).value
        log.info(f"[get_secret|out] => {_result}")
        return _result

