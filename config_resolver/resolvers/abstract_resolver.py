import logging
from abc import ABC, abstractmethod

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