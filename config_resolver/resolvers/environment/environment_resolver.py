import logging
import os

from config_resolver.resolvers.abstract_resolver import AbstractResolver

log = logging.getLogger(__name__)


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