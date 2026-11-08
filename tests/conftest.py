"""Starts the mock API once for the whole test session, before any test module is imported.

config.Config asks the API for the node id (GET /nodes/dispatcher/me) at import time, so the mock has to be up and
API has to point at it before anything imports config. pytest loads this file first, which guarantees that."""
import os
import socket
import threading
import time

import pytest
import uvicorn

from tests import mock_api

with socket.socket() as _s:
    _s.bind(("127.0.0.1", 0))
    _PORT = _s.getsockname()[1]

# Env wins over .env (load_dotenv does not override), so config picks these up
os.environ["API"] = f"http://127.0.0.1:{_PORT}"
os.environ.setdefault("IP", "127.0.0.1")

_server = uvicorn.Server(uvicorn.Config(mock_api.app, host="127.0.0.1", port=_PORT, log_level="warning"))
_thread = threading.Thread(target=_server.run, daemon=True)
_thread.start()
_deadline = time.time() + 10
while not _server.started:
    if time.time() > _deadline:
        raise RuntimeError("mock API did not start")
    time.sleep(0.05)


@pytest.fixture
def api():
    """The running mock API; yields what it received, cleared for each test."""
    mock_api.RECEIVED["scrapes"].clear()
    mock_api.RECEIVED["images"].clear()
    yield mock_api.RECEIVED


def pytest_sessionfinish(session, exitstatus):
    _server.should_exit = True
    _thread.join(timeout=5)
