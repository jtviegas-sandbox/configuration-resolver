import json
import os

import pytest

from configuration_resolver.resolver import Configuration

RESOURCES_DIR = f"{os.path.dirname(os.path.realpath(__file__))}/resources"
JSON_FILE = f"{RESOURCES_DIR}/config_01.json"
JSON_FILES = [f"{RESOURCES_DIR}/config_01.json", f"{RESOURCES_DIR}/config_02.json"]


@pytest.mark.skip
def test_type_error():
    with pytest.raises(TypeError) as x:
        Configuration.init(1234)
    assert "1234 is neither a list nor a string" == str(x.value)


@pytest.mark.skip
def test_value_error():
    with pytest.raises(ValueError) as x:
        Configuration.init("not_a_file")
    assert "not_a_file is neither a file nor a folder" == str(x.value)


def test_one_level_dict():
    impl = Configuration.get_instance()
    assert impl.get("server.url") == impl.get("SERVER_URL") \
           == "http://www.site.com"


def test_singleton_no_overriding():
    impl = Configuration.get_instance()
    impl2 = Configuration.init(JSON_FILE, variables={"local": {"var1": "aaa"}}, config_file_filter_keys=["dev"])
    assert impl == impl2, "not a singleton"
    assert impl.get("local.var1") == impl2.get("LOCAL_VAR1") == "zzs", "wrong value in singleton"


def test_one_level_obj():
    impl = Configuration.get_instance()
    _expected_dict = {"resources": {"color": "yellow", "cpu": "1xc", "mem": 9192, "timeout": 6}, "url": "http://www.site.com"}
    assert sorted(impl.get("server").items())  == sorted(impl.get("SERVER").items()) \
           == sorted(_expected_dict.items())


def test_two_level_dict():
    impl = Configuration.get_instance()
    assert impl.get("server.resources.color") == impl.get("SERVER_RESOURCES_COLOR") == "yellow"


def test_two_level_obj():
    impl = Configuration.get_instance()
    _expected_dict = {"color": "yellow", "cpu": "1xc", "mem": 9192, "timeout": 6}

    assert sorted(impl.get("server.resources").items()) == sorted(impl.get("SERVER_RESOURCES").items()) \
           == sorted(_expected_dict.items())


def test_first_level_text():
    impl = Configuration.get_instance()
    assert impl.get("name") == impl.get("NAME") == "myname"


def test_first_level_number():
    impl = Configuration.get_instance()
    assert impl.get("id") == impl.get("ID") == 12345


def test_first_level_array():
    impl = Configuration.get_instance()
    assert impl.get("tags") == impl.get("TAGS") == ["server", "api"]


def test_base_vars_depth():
    impl = Configuration.get_instance()
    assert impl.get("dag.default.retry_delay") == impl.get("DAG_DEFAULT_RETRY_DELAY") == 5


def test_base_vars_dict():
    impl = Configuration.get_instance()
    _expected_dict = {"default": {"retry_delay": 5}}
    _expected_json = json.dumps(_expected_dict)
    assert json.dumps(impl.get("dag")) == json.dumps(impl.get("DAG")) == _expected_json


def test_filter_key_no_key():
    with pytest.raises(LookupError) as x:
        impl = Configuration.get_instance()
        impl.get("SERVER_RESOURCES_MEMX")
    assert "key SERVER_RESOURCES_MEMX not found" == str(x.value)


def test_filter_key_multiple_sources():
    impl = Configuration()
    assert impl.get("OTHER_VAR1") == "GOLD"
    assert impl.get("OTHER_VAR2") == "SILVER"
    assert impl.get("OTHER_VAR3") == "BRONZE"
    assert impl.get("OTHER_VAR4") == "TIN"
    assert impl.get("OTHER_VAR5") == "C"
    assert impl.get("OTHER_VAR6") == "WATER"
    assert impl.get("OTHER_VAR7") == "1000"
    assert impl.get("OTHER_VAR8") == "STEEL"

