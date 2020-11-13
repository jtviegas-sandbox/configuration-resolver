import logging

from pyspark.sql import SparkSession
from config_resolver.overriders.abstract_overrider import AbstractOverrider

log = logging.getLogger(__name__)


class SparkKeyVaultOverrider(AbstractOverrider):

    def __init__(self, config: dict):
        log.debug(f"[__init__|in] ({[k + ':' + v[0:3] for k, v in config.items()]}")

        AbstractOverrider.validate_configuration(['keyvault_scope'], config)
        self.__dbutils = SparkKeyVaultOverrider.get_dbutils()
        self.__scope = config["keyvault_scope"]

        log.debug(f"[__init__|out]")

    def get(self, key) -> str:
        log.debug(f"[get|in] ({key})")
        result = None
        upper_key = key.upper().replace('_', '-')
        try:
            result = self.__dbutils.secrets.get(self.__scope, upper_key)
        except Exception as x:
            log.debug(f"secret not found: {upper_key}", exc_info=x)
        log.debug(f"[get|out] => {result[0:3] if result is not None else 'None'}")
        return result

    @staticmethod
    def get_dbutils():
        log.debug("[_get_dbutils|in]")
        dbutils = None
        spark = SparkSession.builder.getOrCreate()
        if spark.conf.get("spark.databricks.service.client.enabled") == "true":
            from pyspark.dbutils import DBUtils
            dbutils = DBUtils(spark)
            log.info("[_get_dbutils] got it from spark")
        else:
            import IPython
            dbutils = IPython.get_ipython().user_ns["dbutils"]
            log.info("[_get_dbutils] got it from IPython")

        log.debug(f"[_get_dbutils|out] => {dbutils}")
        return dbutils
