import json
import os

import pytest
from configuration_overrider.abstract_overrider import AbstractOverrider

from config_resolver.resolver import Configuration

RESOURCES_DIR = f"{os.path.dirname(os.path.realpath(__file__))}/resources"
JSON_FILE = f"{RESOURCES_DIR}/config_01.json"
JSON_FILES = [f"{RESOURCES_DIR}/config_01.json", f"{RESOURCES_DIR}/config_02.json"]


class DummyOverrider(AbstractOverrider):

    def __init__(self, key: str, value: str):
        self.__key = key
        self.__value = value

    def get(self, key) -> str:
        _result = None
        if key == self.__key:
            _result = self.__value
        return _result


def test_type_error():
    with pytest.raises(TypeError) as x:
        Configuration.get_instance(1234)
    assert "1234 is neither a list nor a string" == str(x.value)


def test_value_error():
    with pytest.raises(ValueError) as x:
        Configuration.get_instance("not_a_file")
    assert "not_a_file is neither a file nor a folder" == str(x.value)


def test_one_level_dict():
    impl = Configuration.get_instance(JSON_FILE)
    assert impl.get("server.url") == impl.get("SERVER_URL") \
           == "http://www.site.com"


def test_one_level_obj():
    impl = Configuration.get_instance(JSON_FILE)
    _expected_dict = {"url": "http://www.site.com", "resources": { "mem": 2048 } }
    _expected_json = json.dumps(_expected_dict)
    assert json.dumps(impl.get("server")) == json.dumps(impl.get("SERVER")) \
           == _expected_json


def test_two_level_dict():
    impl = Configuration(JSON_FILE)
    assert impl.get("server.resources.mem") == impl.get("SERVER_RESOURCES_MEM") == 2048


def test_two_level_obj():
    impl = Configuration(JSON_FILE)
    _expected_dict = { "mem": 2048 }
    _expected_json = json.dumps(_expected_dict)
    assert json.dumps(impl.get("server.resources")) == json.dumps(impl.get("SERVER_RESOURCES")) \
           == _expected_json


def test_first_level_text():
    impl = Configuration(JSON_FILE)
    assert impl.get("name") == impl.get("NAME") == "myname"


def test_first_level_number():
    impl = Configuration(JSON_FILE)
    assert impl.get("id") == impl.get("ID") == 12345


def test_first_level_array():
    impl = Configuration(JSON_FILE)
    assert impl.get("tags") == impl.get("TAGS") == ["server", "api"]


def test_override_by_environment_check_dict():
    impl = Configuration.get_instance(JSON_FILE, variables={"server": {"resources": {"cpu": "1xc"}}, "id": 1},
                                      variable_overriders=[DummyOverrider("SERVER_RESOURCES_MEM", "9192")])
    expected = {"cpu": "1xc", "mem": "9192"}
    assert impl.get("server.resources.mem") == impl.get("SERVER_RESOURCES_MEM") == '9192'
    assert impl.get("server.resources") == impl.get("SERVER_RESOURCES") == expected


def test_base_vars_depth():
    impl = Configuration(JSON_FILE, variables={"dag": {"default": {"retry_delay": 5}}, "id": 1})
    print(impl)
    assert impl.get("dag.default.retry_delay") == impl.get("DAG_DEFAULT_RETRY_DELAY") == 5


def test_base_vars_dict():
    impl = Configuration(JSON_FILE, variables={"dag": {"default": {"retry_delay": 5}}, "id": 1})
    _expected_dict = {"default": {"retry_delay": 5}}
    _expected_json = json.dumps(_expected_dict)
    assert json.dumps(impl.get("dag")) == json.dumps(impl.get("DAG")) == _expected_json


def test_base_vars_dict_composition():
    impl = Configuration(JSON_FILE, variables={"server": {"resources": {"cpu": "1xc"}}, "id": 1})
    _expected_dict = {"cpu": "1xc", "mem": 2048}
    _expected_json = json.dumps(_expected_dict)
    assert json.dumps(impl.get("server.resources")) == json.dumps(impl.get("SERVER_RESOURCES")) == _expected_json


def test_filter_key():
    impl = Configuration.get_instance(JSON_FILE, variables={"server": {"resources": {"cpu": "1xc"}}, "id": 1},
                                      config_file_filter_keys=["server", "dev"],
                                      variable_overriders=[DummyOverrider("BIG_PSWD", "notdummy")])
    expected = {"cpu": "1xc"}
    assert impl.get("server.resources") == impl.get("SERVER_RESOURCES") == expected
    assert impl.get("VAR1") == "aix"


def test_filter_key_no_key():
    with pytest.raises(LookupError) as x:
        impl = Configuration.get_instance(JSON_FILE, variables={"server": {"resources": {"cpu": "1xc"}}, "id": 1},
                                          config_file_filter_keys=["server"])
        impl.get("SERVER_RESOURCES_MEM")
    assert "key SERVER_RESOURCES_MEM not found" == str(x.value)


def test_filter_key_multiple_sources():
    impl = Configuration.get_instance(JSON_FILES, variables={"server": {"resources": {"cpu": "1xc"}}, "id": 1},
                                      config_file_filter_keys=["server", "local", "common"],
                                      variable_overriders=[DummyOverrider("BIG_PSWD", "notdummy")])
    expected = {"cpu": "1xc"}
    assert impl.get("server.resources") == impl.get("SERVER_RESOURCES") == expected
    assert impl.get("VAR1") == "zzs"
    assert impl.get("VAR3") == "SILVER"
    assert impl.get("VAR4") == "water"


def test_filter_key_multiple_sources_with_env():
    impl = Configuration.get_instance(JSON_FILES, variables={"server": {"resources": {"cpu": "1xc"}}, "id": 1},
                                      variable_overriders=[DummyOverrider("big_pswd", "notdummy")])
    assert impl.get("big_pswd") == "notdummy"

