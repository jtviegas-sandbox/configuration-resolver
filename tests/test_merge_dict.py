import json

from config_resolver.resolvers.utils_dict import merge_dict, flatten_dict


def test_merge():
    x = {"server": {"resources": {"mem": 2048}}, "name": "zenao", "tags": ["belo", "abstruso"]}
    y = {"server": {"resources": {"cpu": "1xc"}}, "id": 1, "tags": ["yellow"]}
    expected = json.dumps({"server": {"resources": {"cpu": "1xc", "mem": 2048}}, "id": 1, "name": "zenao", "tags": ["belo", "abstruso", "yellow"]})
    merge_dict(x, y)
    assert sorted(json.dumps(y)) == sorted(expected)


def test_flatten():
    input_var = {"server": {"resources": {"cpu": "1xc", "mem": 2048}, "id": 1}, "name": "zenao",
                           "tags": ["belo", "abstruso", "yellow"]}
    expected = {"SERVER": {"resources": {"cpu": "1xc", "mem": 2048}, "id": 1},
                "SERVER_RESOURCES": {"cpu": "1xc", "mem": 2048},
                "SERVER_RESOURCES_CPU": "1xc", "SERVER_RESOURCES_MEM": 2048, "SERVER_ID": 1,
                "NAME": "zenao", "TAGS": ["belo", "abstruso", "yellow"]}
    output = {}
    flatten_dict(input_var, output)
    assert sorted(output) == sorted(expected)
