import logging
from typing import List

log = logging.getLogger(__name__)


def merge_dict(source: dict, target: dict = None):
    log.info(f"[merge_dict|in] ({source}, {target})")
    pointer = None
    if source is None:
        raise ValueError(f"mandatory to provide at least the source")

    if target is None:
        return {**source}

    for key in source.keys():
        value = source[key]
        value_type = type(value).__name__
        pointer = {} if target is None else target
        if value_type == 'dict':
            if key not in pointer.keys():
                pointer[key] = {}
            merge_dict(value, pointer[key])
        elif value_type == 'list' and key in pointer.keys() and type(pointer[key]).__name__ == 'list':
            pointer[key].extend(value)
        else:
            log.info(f"[merge_dict] adding new entry {key}: {value}")
            pointer[key] = value

    log.info(f"[merge_dict|out] => {pointer}")


def flatten_dict(source: dict, target: dict, prefix: str = None):
    log.info(f"[flatten_dict|in] ({source})")

    if source is None:
        raise ValueError("no dict")

    for key in source.keys():
        value = source[key]
        value_type = type(value).__name__
        new_flattened_key = f"{key.upper()}" if prefix is None else f"{prefix}_{key.upper()}"
        if value_type == 'dict':
            flatten_dict(value, target, new_flattened_key)

        log.info(f"[flatten_dict] adding new entry {key}: {value}")
        target[new_flattened_key] = value

    log.info(f"[flatten_dict|out] => {source}")


def merge_flattened(source: dict, target: dict):
    log.info(f"[merge_flattened|in] ({source}, {target})")

    for key, value in source.items():
        components = key.split(sep="_")
        dict_pointer = target
        match = False
        for index, component in enumerate(components):
            new_key = component.lower()
            if new_key not in dict_pointer.keys():
                match = False
                break
            elif index == len(components) - 1 :
                # last one
                match = True
            else:
                dict_pointer = dict_pointer[new_key]
                match = True

        if match:
            dict_pointer[new_key] = value

    log.info(f"[merge_flattened|out] => {target}")


def find_config_entries(config: str, target: dict):
    log.info(f"[find_config_entries|in] ({config}, {target})")
    find_result = []
    variable = config.upper()
    if 0 == config.count('.'):
        find_variable(config, target, find_result)
    else:
        find_property(config, target, find_result)
        variable = config.replace('.', '_').upper()

    if 1 < len(find_result):
        raise Exception("can't have more than one result, please review your configuration source")

    result = [{'pointer': target, 'key': variable}, *find_result]

    log.info(f"[find_config_entries|out] => {result}")
    return result

def find_variable(var: str, target: dict, result: List[dict]):
    log.info(f"[find_variable|in] ({var}, {target}, {result})")

    components = var.split(sep="_")
    query=''
    for index, component in enumerate(components):
        query += component.lower() if 0 == len(query) else '_' + component.lower()
        if query in target.keys():
            if index + 1 == len(components):
                result.append( {'pointer': target, 'key': query} )
            else:
                find_variable( '_'.join(components[index+1:]), target[query], result)

    log.info(f"[find_variable|out] => {result}")


def find_property(key: str, target: dict, result: List[dict]):
    log.info(f"[find_property|in] ({key}, {target}, {result})")

    components = key.split(sep=".")

    for index, component in enumerate(components):

        if component in target.keys():
            if index + 1 == len(components):
                result.append( {'pointer': target, 'key': component} )
            else:
                find_property( '.'.join(components[index+1:]), target[component], result)

    log.info(f"[find_property|out] => {result}")