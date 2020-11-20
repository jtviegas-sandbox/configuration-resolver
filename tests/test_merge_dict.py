import json

import pytest

from configuration_resolver.overriders.utils_dict import merge_dict, flatten_dict, merge_flattened, find_variable, \
    find_property, find_config_entries


def test_merge():
    x = {"server": {"resources": {"mem": "2048"}}, "name": "zenao", "tags": ["belo", "abstruso"]}
    y = {"server": {"resources": {"cpu": "1xc"}}, "id": "1", "tags": ["yellow"]}
    expected = {"server": {"resources": {"cpu": "1xc", "mem": "2048"}}, "id": "1", "name": "zenao", "tags": ["yellow", "belo", "abstruso"]}
    merge_dict(x, y)
    sorted_y = {k[0]: k[1] for k in sorted(y.items())}
    sorted_expected = {k[0]: k[1] for k in sorted(expected.items())}
    assert sorted_y == sorted_expected


def test_flatten():
    input_var = {"server": {"resources": {"cpu": "1xc", "mem": "2048"}, "id": "1"}, "name": "zenao",
                           "tags": ["belo", "abstruso", "yellow"]}
    expected = {"SERVER": {"resources": {"cpu": "1xc", "mem": "2048"}, "id": "1"},
                "SERVER_RESOURCES": {"cpu": "1xc", "mem": "2048"},
                "SERVER_RESOURCES_CPU": "1xc", "SERVER_RESOURCES_MEM": "2048", "SERVER_ID": "1",
                "NAME": "zenao", "TAGS": ["belo", "abstruso", "yellow"]}
    output = {}
    flatten_dict(input_var, output)
    sorted_output = {k[0]: k[1] for k in sorted(output.items())}
    assert sorted_output == expected


def test_merge_flattened():
    actual = {"server": {"resources": {"cpu": "1xc", "mem": "2048"}, "id": "1"}, "name": "zenao",
                 "tags": ["belo", "abstruso", "yellow"]}
    expected = {"server": {"resources": {"cpu": "1xc", "mem": "4096"}, "id": "3"}, "name": "zenao",
                 "tags": ["belo", "abstruso", "yellow"]}

    merge_flattened({"SERVER_RESOURCES_MEM": "4096", "SERVER_ID": "3"}, actual)
    sorted_output = {k[0]: k[1] for k in sorted(actual.items())}
    assert sorted_output == expected


def test_find_variable():
    d = {"var1": {"big_pswd": {"cpu": "1xc"}, "big": {"pswd": "1234"}}}
    result = []
    find_variable("VAR1_BIG_PSWD", d, result)
    assert 2 == len(result)


def test_find_property():
    d = {"var1": {"big_pswd": {"cpu": "1xc"}, "big": {"pswd": "1234"}}}
    result = []
    find_property("var1.big_pswd", d, result)
    assert 1 == len(result)
    result = []
    find_property("var1.big_pswd.cpu", d, result)
    assert 1 == len(result)
    result = []
    find_property("var1.big.pswd", d, result)
    assert 1 == len(result)


def test_config_entries_too_many():
    d = {"var1": {"big_pswd": {"cpu": "1xc"}, "big": {"pswd": "1234"}}}
    with pytest.raises(Exception) as x:
        find_config_entries("VAR1_BIG_PSWD", d)
        assert "can't have more than one result, please review your configuration source" \
               == str(x.value)


def test_config_entries():
    d = {"var1": {"big_pswd": {"cpu": "1xc"}, "big": {"pswdx": "1234"}}}
    result = find_config_entries("VAR1_BIG_PSWD", d)
    assert 2 == len(result)