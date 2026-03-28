#!/usr/bin/env python3
"""
Pytest configuration and shared fixtures for Phantom/MetasploitMCP tests.
"""
import sys
import os
import pytest
import logging
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch

# 1. Path Setup: Add project root to Python path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "src"))

def pytest_configure(config):
    """Configure pytest with custom settings and global mocks."""
    # Mock external dependencies that might not be in the environment
    mock_modules = [
        'uvicorn', 'fastapi', 'mcp.server.fastmcp', 'mcp.server.sse',
        'pymetasploit3.msfrpc', 'starlette.applications',
        'starlette.routing', 'mcp.server.session'
    ]
    for module in mock_modules:
        if module not in sys.modules:
            sys.modules[module] = Mock()

def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on filename or name."""
    for item in items:
        # Categorize by nodeid (filename/path)
        if any(x in item.nodeid for x in ["test_options", "test_helpers"]):
            item.add_marker(pytest.mark.unit)
        if "test_tools_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)

        # Categorize by function name
        name = item.name.lower()
        if "network" in name:
            item.add_marker(pytest.mark.network)
        if any(kw in name for kw in ["slow", "timeout", "long"]):
            item.add_marker(pytest.mark.slow)

# --- Fixtures ---

@pytest.fixture(scope="session")
def mock_msf_environment():
    """Provides a session-scoped mock Metasploit RPC environment."""
    class MockMsfClient:
        def __init__(self, *args, **kwargs):
            self.modules = Mock(exploits=[], payloads=[])
            self.core = Mock(version={'version': '6.3.0'})
            self.sessions = Mock(list=Mock(return_value={}))
            self.jobs = Mock(list=Mock(return_value={}))
            self.consoles = Mock()

    class MockMsfConsole:
        def __init__(self, cid='test-console'):
            self.cid = cid
        def read(self): return {'data': '', 'prompt': 'msf6 > ', 'busy': False}
        def write(self, cmd): return True

    mock_data = {
        'MsfRpcClient': MockMsfClient,
        'MsfConsole': MockMsfConsole,
        'MsfRpcError': type('MockMsfRpcError', (Exception,), {})
    }

    with patch.dict('sys.modules', {'pymetasploit3.msfrpc': Mock(**mock_data)}):
        yield mock_data

@pytest.fixture
def mock_logger():
    """Mocks the project-level logger."""
    with patch('MetasploitMCP.logger') as mock_log:
        yield mock_log

@pytest.fixture
def temp_payload_dir(tmp_path):
    """Provides a clean directory for payload testing."""
    payload_dir = tmp_path / "payloads"
    payload_dir.mkdir()
    with patch('MetasploitMCP.PAYLOAD_SAVE_DIR', str(payload_dir)):
        yield payload_dir

@pytest.fixture
def capture_logs(caplog):
    """Utility to capture logs at DEBUG level."""
    caplog.set_level(logging.DEBUG)
    return caplog

# --- CLI Options & Hooks ---

def pytest_addoption(parser):
    """Add custom CLI flags for test filtering."""
    parser.addoption("--run-slow", action="store_true", default=False, help="run slow tests")
    parser.addoption("--run-network", action="store_true", default=False, help="run network tests")

def pytest_runtest_setup(item):
    """Skip tests based on CLI flags."""
    markers = {
        "slow": "--run-slow",
        "network": "--run-network"
    }
    for marker, option in markers.items():
        if marker in item.keywords and not item.config.getoption(option):
            pytest.skip(f"Test requires {option} to run")

@pytest.fixture(autouse=True)
def reset_global_state():
    """Ensures a clean state for legacy tests when that module exists."""
    try:
        with patch('MetasploitMCP.MetasploitMCP._instance', None):
            yield
    except ModuleNotFoundError:
        yield
