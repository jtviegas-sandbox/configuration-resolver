import json
import logging
import os
from typing import Union, List

from config_resolver.overriders.utils_dict import merge_dict

log = logging.getLogger(__name__)


class FileSysConfiguration:

    def __init__(self, fs_refs: Union[list, str], data: dict = None, filter_keys: List[str] = []):
        log.info(f"[__init__|in] ({fs_refs})")
        self.__fs_refs = fs_refs
        self.__data = {} if data is None else data
        self.__filter_keys = filter_keys
        log.info(f"[__init__|out]")

    def read(self) -> str:
        log.info(f"[get|in]")

        input_type = type(self.__fs_refs).__name__
        if input_type == 'str':
            if os.path.isdir(self.__fs_refs):
                self.__handle_dir(self.__fs_refs)
            elif os.path.isfile(self.__fs_refs):
                self.__handle_file(self.__fs_refs)
            else:
                raise ValueError(f"{self.__fs_refs} is neither a file nor a folder")
        elif input_type == 'list':
            self.__handle_array(self.__fs_refs)
        else:
            raise TypeError(f"{self.__fs_refs} is neither a list nor a string")

        log.info(f"[get|out] => {self.__data}")
        return self.__data

    def __process_file(self, source: str):
        log.info(f"[process_file|in] ({source})")

        with open(source) as json_file:
            # json content is in itself a dict
            content = json.load(json_file)
            if 0 < len(self.__filter_keys):
                # we must filter first level keys in the dict
                filtered_content = {}
                for filter_key in self.__filter_keys:
                    if filter_key in content.keys():
                        filtered_entry = content[filter_key]
                        filtered_entry_type = type(filtered_entry).__name__
                        if filtered_entry_type != 'dict':
                            raise ValueError(f"filter key:{filter_key} does not correspond to a nested dict")
                        else:
                            filtered_content.update(filtered_entry)
                content = filtered_content
            merge_dict(content, self.__data)

        log.info(f"[process_file|out]")

    def __handle_array(self, source: list):
        log.info(f"[handle_array|in] ({source})")

        for entry in source:
            if os.path.isdir(entry):
                self.__handle_dir(entry)
            elif os.path.isfile(entry):
                self.__handle_file(entry)
            else:
                raise ValueError(f"{entry} is neither a file nor a folder")

        log.info(f"[handle_array|out]")

    def __handle_file(self, source: str):
        log.info(f"[handle_file|in] ({source})")

        if source.endswith(".json") or source.endswith(".JSON"):
            self.__process_file(source)
        else:
            raise ValueError(f"{source} is not a json file")

        log.info(f"[handle_file|out]")

    def __handle_dir(self, source: str):
        log.info(f"[handle_dir|in] ({source})")

        for file in os.listdir(source):
            entry = os.path.join(source, file)
            if os.path.isdir(entry):
                self.__handle_dir(entry)
            elif os.path.isfile(entry):
                self.__handle_file(entry)
            else:
                raise ValueError(f"{entry} is neither a file nor a folder")

        log.info(f"[handle_dir|out]")



