from configuration_overrider.abstract_overrider import AbstractOverrider


class DummyOverrider(AbstractOverrider):

    def __init__(self, key: str, value: str):
        self.__key = key
        self.__value = value

    def get(self, key) -> str:
        _result = None
        if key == self.__key:
            _result = self.__value
        return _result