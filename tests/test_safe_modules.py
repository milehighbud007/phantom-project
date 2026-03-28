#!/usr/bin/env python3
"""
Safe tests for current non-operational package modules.
"""

from __future__ import annotations

import asyncio
import importlib
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from phantom.database import CampaignDatabase
from phantom.probe_helper import ProbeError, _parse_ndjson, probe_ips
from phantom.msf.rpc_client import MSFRPCClient


class DummyHTTPException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class DummyAPIRouter:
    def __init__(self, *args, **kwargs):
        pass

    def get(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator


def load_routes_module():
    fastapi_stub = Mock()
    fastapi_stub.APIRouter = DummyAPIRouter
    fastapi_stub.HTTPException = DummyHTTPException
    fastapi_stub.Query = lambda default=..., **kwargs: default

    with patch.dict(sys.modules, {"fastapi": fastapi_stub}):
        import phantom.routes as routes_module
        return importlib.reload(routes_module)


def test_parse_ndjson_returns_last_object():
    raw = '\n{"status":"ignored"}\n{"status":"ok","count":2}\n'
    result = _parse_ndjson(raw)
    assert result == {"status": "ok", "count": 2}


def test_parse_ndjson_rejects_empty_input():
    with pytest.raises(ProbeError, match="empty response"):
        _parse_ndjson("\n \n")


def test_parse_ndjson_rejects_invalid_json():
    with pytest.raises(ProbeError, match="Failed to parse"):
        _parse_ndjson("not-json")


def test_probe_ips_rejects_empty_ip_list(tmp_path):
    with pytest.raises(ProbeError, match="cannot be empty"):
        probe_ips([], socket_path=str(tmp_path / "socket"))


def test_probe_ips_rejects_missing_socket(tmp_path):
    with pytest.raises(ProbeError, match="Socket not found"):
        probe_ips(["192.0.2.10"], socket_path=str(tmp_path / "missing.sock"))


def test_campaign_database_records_failures_and_audit_log(tmp_path):
    database = CampaignDatabase(str(tmp_path / "campaigns.db"))
    database.create_campaign("cmp-002", "192.0.2.11")
    database.log_exploit_result(
        "cmp-002",
        {
            "exploit": "demo/failure",
            "status": "failed",
            "error": "boom",
        },
    )
    database.log_audit("scan", "192.0.2.11", "ok", "unit-test")

    details = database.get_campaign_details("cmp-002")
    assert details is not None
    assert details["fail_count"] == 1
    assert details["success_count"] == 0
    assert details["results"][0]["error"] == "boom"

    with database.connection() as conn:
        audit = conn.execute("SELECT action, target, result, details FROM audit_logs").fetchone()
    assert dict(audit) == {
        "action": "scan",
        "target": "192.0.2.11",
        "result": "ok",
        "details": "unit-test",
    }


def test_get_all_campaigns_respects_limit_and_sort_order(tmp_path):
    database = CampaignDatabase(str(tmp_path / "campaigns.db"))
    database.create_campaign("cmp-early", "192.0.2.20")
    database.create_campaign("cmp-late", "192.0.2.21")

    campaigns = database.get_all_campaigns(limit=1)
    assert len(campaigns) == 1
    assert campaigns[0]["id"] == "cmp-late"


def test_create_app_builds_without_optional_nmap_dependency(tmp_path):
    project_root = Path(__file__).resolve().parents[1]
    src_path = str(project_root / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    with patch.dict(sys.modules, {"nmap": None}):
        import phantom.app as app_module

        for handler in list(app_module.logger.handlers):
            app_module.logger.removeHandler(handler)
            handler.close()

        with patch.object(app_module.config, "LOG_FILE", str(tmp_path / "phantom.log")):
            flask_app = app_module.create_app()
            client = flask_app.test_client()

            response = client.get("/")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "online"
    assert payload["attack_system_ready"] is False


def test_metasploit_provider_login_success_sets_token():
    from phantom.app import MetasploitProvider

    provider = MetasploitProvider()
    provider._call = Mock(return_value={"token": "abc123"})

    assert provider.login() is True
    assert provider.token == "abc123"


def test_rpc_client_pack_and_unpack_round_trip():
    client = MSFRPCClient()
    payload = client._pack("core.version", ["token", 1])
    unpacked = client._unpack(payload)
    assert unpacked == ["core.version", "token", 1]


def test_rpc_client_login_sets_token_on_success():
    client = MSFRPCClient()
    client.call = Mock(return_value={"result": "success", "token": "tok-1"})

    assert client.login() is True
    assert client.token == "tok-1"


def test_rpc_client_call_adds_token_for_authenticated_requests():
    client = MSFRPCClient()
    client.token = "tok-2"
    client._pack = Mock(return_value=b"payload")
    client._unpack = Mock(return_value={"ok": True})
    response = Mock()
    response.content = b"ignored"
    response.raise_for_status = Mock()
    client.session.post = Mock(return_value=response)

    result = client.call("core.version", [])

    assert result == {"ok": True}
    client._pack.assert_called_once_with("core.version", ["tok-2"])


def test_rpc_client_call_returns_error_dict_on_exception():
    client = MSFRPCClient()
    client.session.post = Mock(side_effect=RuntimeError("rpc down"))

    result = client.call("core.version", [])

    assert result["error"] is True
    assert "rpc down" in result["message"]


def test_rpc_client_retries_after_token_error():
    client = MSFRPCClient()
    client.token = "expired"
    first_response = {"error": True, "error_message": "token expired"}
    second_response = {"result": "success"}
    client._unpack = Mock(side_effect=[first_response, second_response])
    response = Mock()
    response.content = b"ignored"
    response.raise_for_status = Mock()
    client.session.post = Mock(return_value=response)
    client.login = Mock(return_value=True)

    result = client.call("core.version", [])

    assert result == second_response
    assert client.login.call_count == 1
    assert client.session.post.call_count == 2


def test_routes_list_modules_disconnected():
    routes_module = load_routes_module()

    service = Mock()
    service.is_connected.return_value = False

    with patch.object(routes_module, "get_mcp_service", return_value=service):
        result = asyncio.run(routes_module.list_modules())

    assert result == {"modules": [], "status": "disconnected"}


def test_routes_list_modules_connected():
    routes_module = load_routes_module()

    service = Mock()
    service.is_connected.return_value = True
    service.find_modules_by_keyword.return_value = ["exploit/demo"]

    with patch.object(routes_module, "get_mcp_service", return_value=service):
        result = asyncio.run(routes_module.list_modules())

    assert result == {"modules": ["exploit/demo"], "count": 1}


def test_routes_get_module_returns_metadata():
    routes_module = load_routes_module()

    service = Mock()
    service.is_connected.return_value = True
    service.get_module_meta.return_value = {
        "description": "demo",
        "references": ["CVE-2020-0001"],
        "options": {"RHOSTS": {}, "RPORT": {}},
    }

    with patch.object(routes_module, "get_mcp_service", return_value=service):
        result = asyncio.run(routes_module.get_module("exploit/windows/demo"))

    assert result["name"] == "exploit/windows/demo"
    assert result["type"] == "exploit"
    assert result["options"] == ["RHOSTS", "RPORT"]


def test_routes_list_sessions_supports_callable_session_list():
    routes_module = load_routes_module()

    service = Mock()
    service.is_connected.return_value = True
    service.client.sessions.list = Mock(return_value={"1": {"type": "shell"}})

    with patch.object(routes_module, "get_mcp_service", return_value=service):
        result = asyncio.run(routes_module.list_sessions())

    assert result == {"sessions": {"1": {"type": "shell"}}, "count": 1}


def test_routes_health_check_uses_service_state():
    routes_module = load_routes_module()

    service = Mock()
    service.is_connected.return_value = True
    service.host = "127.0.0.1"
    service.port = 55553

    with patch.object(routes_module, "get_mcp_service", return_value=service):
        result = asyncio.run(routes_module.health_check())

    assert result == {"status": "online", "host": "127.0.0.1", "port": 55553}
