import uuid

import httpx

import config
from client.node import get_node
from tests import mock_api


def test_me_returns_plaintext_uuid():
    r = httpx.get(config.Config.API + "/nodes/dispatcher/me")

    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/plain")
    assert str(uuid.UUID(r.text)) == r.text == mock_api.NODE_ID


def test_get_node_uses_me_route():
    node = get_node()

    assert node.node_id == mock_api.NODE_ID
    assert node.ip == "127.0.0.1"


def test_config_node_id_comes_from_me_route():
    # Config resolves the node at import time, against the mock started in conftest.py
    assert config.Config.NODE.node_id == mock_api.NODE_ID
