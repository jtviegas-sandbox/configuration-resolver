from unittest.mock import patch

import pytest
import os
import json

from config_resolver.resolvers.azure_keyvault.azure_keyvault_reader import AzureKeyVaultReader
from config_resolver.resolver import Configuration, EnvironmentResolver

RESOURCES_DIR = f"{os.path.dirname(os.path.realpath(__file__))}/resources"
JSON_FILE = f"{RESOURCES_DIR}/config_01.json"
AZURE_TENANT_ID="5a9a19f5-40ed-4f04-b7d0-09a3d36e87da"
AZURE_CLIENT_ID="d4478504-2d43-4cb1-ba06-b413a1c12bf0"
AZURE_KEYVAULT_URL="https://config-resolver-dev.vault.azure.net/"
AZURE_CLIENT_SECRET="dummy"


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


def test_override_by_secret():
    az_keyvault_config = {'tenant_id': AZURE_TENANT_ID,
                          'client_id': AZURE_CLIENT_ID,
                          'vault_url': AZURE_KEYVAULT_URL,
                          'client_secret': AZURE_CLIENT_SECRET}
    with patch.object(AzureKeyVaultReader, 'get_secret', autospec=True) as mock_keyvault:
        mock_keyvault.return_value = '4096'
        impl = Configuration.get_instance(JSON_FILE, az_keyvault_config=az_keyvault_config)
        assert impl.get("server.resources.mem") == impl.get("SERVER_RESOURCES_MEM") == '4096'


def test_override_by_environment():
    az_keyvault_config = {'tenant_id': AZURE_TENANT_ID,
                          'client_id': AZURE_CLIENT_ID,
                          'vault_url': AZURE_KEYVAULT_URL,
                          'client_secret': AZURE_CLIENT_SECRET}
    with patch.object(AzureKeyVaultReader, 'get_secret', autospec=True) as mock_keyvault:
        with patch.object(EnvironmentResolver, 'get', autospec=True) as mock_env:
            mock_keyvault.return_value = '4096'
            mock_env.return_value = '9192'
            impl = Configuration.get_instance(JSON_FILE, az_keyvault_config=az_keyvault_config)
            assert impl.get("server.resources.mem") == impl.get("SERVER_RESOURCES_MEM") == '9192'


def test_base_vars_depth():
    impl = Configuration(JSON_FILE, base_vars={"dag": {"default": {"retry_delay": 5}}, "id": 1})
    assert impl.get("dag.default.retry_delay") == impl.get("DAG_DEFAULT_RETRY_DELAY") == 5


def test_base_vars_dict():
    impl = Configuration(JSON_FILE, base_vars={"dag": {"default": {"retry_delay": 5}}, "id": 1})
    _expected_dict = {"default": {"retry_delay": 5}}
    _expected_json = json.dumps(_expected_dict)
    assert json.dumps(impl.get("dag")) == json.dumps(impl.get("DAG")) == _expected_json


def test_base_vars_dict_composition():
    impl = Configuration(JSON_FILE, base_vars={"server": {"resources": {"cpu": "1xc"}}, "id": 1})
    _expected_dict = {"cpu": "1xc", "mem": 2048}
    _expected_json = json.dumps(_expected_dict)
    assert json.dumps(impl.get("server.resources")) == json.dumps(impl.get("SERVER_RESOURCES")) == _expected_json
