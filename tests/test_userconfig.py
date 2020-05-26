import pathlib

import pytest
from pytest_mock import mocker

from aircheq.userconfig import TomlLoader

def test_TomlLoader_can_be_accessed_by_index():
    toml_path = (
        pathlib.Path(__file__).parent.joinpath("./resources/userconfig/onlyroot.toml").resolve()
    )
    config = TomlLoader(config_path=toml_path)
    print(config)
    assert config["test_value"] == "this is a test"
