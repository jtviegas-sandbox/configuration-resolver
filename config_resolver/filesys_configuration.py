import json
import logging
import os
from typing import Union

log = logging.getLogger(__name__)


class FileSysConfiguration:

    def __init__(self, fs_refs: Union[list, str], var_prefix: str):
        log.info(f"[__init__|in] ({fs_refs},{var_prefix})")
        self.__fs_refs = fs_refs
        self.__var_prefix = var_prefix
        self.__data = {}
        log.info(f"[__init__|out]")

    def read(self) -> str:
        log.info(f"[get|in]")

        input_type = type(self.__fs_refs).__name__
        if input_type == 'str':
            if os.path.isdir(self.__fs_refs):
                self.__handle_dir(self.__fs_refs, self.__var_prefix)
            elif os.path.isfile(self.__fs_refs):
                self.__handle_file(self.__fs_refs, self.__var_prefix)
            else:
                raise ValueError(f"{self.__fs_refs} is neither a file nor a folder")
        elif input_type == 'list':
            self.__handle_array(self.__fs_refs, self.__var_prefix)
        else:
            raise TypeError(f"{self.__fs_refs} is neither a list nor a string")

        log.info(f"[get|out] => {self.__data}")
        return self.__data

    def __process_file(self, source: str, prefix: str):
        log.info(f"[process_file|in] ({source},{prefix})")

        with open(source) as json_file:
            # json content is in itself a dict
            self.__process_dict(json.load(json_file), prefix)

        log.info(f"[process_file|out]")

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

    def __handle_array(self, source: list, prefix: str):
        log.info(f"[handle_array|in] ({source},{prefix})")

        for entry in source:
            if os.path.isdir(entry):
                self.__handle_dir(entry, prefix)
            elif os.path.isfile(entry):
                self.__handle_file(entry, prefix)
            else:
                raise ValueError(f"{entry} is neither a file nor a folder")

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

        for file in os.listdir(source):
            entry = os.path.join(source, file)
            if os.path.isdir(entry):
                self.__handle_dir(entry, prefix)
            elif os.path.isfile(entry):
                self.__handle_file(entry, prefix)
            else:
                raise ValueError(f"{entry} is neither a file nor a folder")

        log.info(f"[handle_dir|out]")



