import logging

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