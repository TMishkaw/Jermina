"""Unit tests for Jemini Studio MCP Server (JSON-RPC stdio protocol)."""

import pytest

from jemini.mcp.server import MCPServer
from jemini.mcp.studio_docs import StudioDocsEngine


@pytest.fixture
def mcp_server():
    return MCPServer(engine=StudioDocsEngine())


def test_mcp_initialize(mcp_server):
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"},
        },
    }
    resp = mcp_server.handle_request(req)
    assert resp["jsonrpc"] == "2.0"
    assert resp["id"] == 1
    assert "result" in resp
    assert resp["result"]["serverInfo"]["name"] == "jemini-studio-docs"
    assert "tools" in resp["result"]["capabilities"]


def test_mcp_ping(mcp_server):
    req = {
        "jsonrpc": "2.0",
        "id": 42,
        "method": "ping",
    }
    resp = mcp_server.handle_request(req)
    assert resp["id"] == 42
    assert resp["result"] == {}


def test_mcp_tools_list(mcp_server):
    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
    }
    resp = mcp_server.handle_request(req)
    assert resp["id"] == 2
    tools = resp["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "jemini_search_docs" in tool_names
    assert "jemini_get_doc" in tool_names
    assert "jemini_list_docs" in tool_names
    assert "jemini_list_sections" in tool_names


def test_mcp_call_search_docs(mcp_server):
    req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "jemini_search_docs",
            "arguments": {
                "query": "WebSocket 1007",
            },
        },
    }
    resp = mcp_server.handle_request(req)
    assert resp["id"] == 3
    content = resp["result"]["content"][0]["text"]
    assert "Search Results for 'WebSocket 1007'" in content
    assert "ConstraintsAndGotchas" in content or "WebSocketStreaming" in content


def test_mcp_call_get_doc(mcp_server):
    req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "jemini_get_doc",
            "arguments": {
                "doc_name": "StickmanKinematics",
            },
        },
    }
    resp = mcp_server.handle_request(req)
    assert resp["id"] == 4
    content = resp["result"]["content"][0]["text"]
    assert "Stickman Kinematics & Rigging Specification" in content

    # Non-existent doc
    req_missing = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "jemini_get_doc",
            "arguments": {
                "doc_name": "NonExistentDoc",
            },
        },
    }
    resp_missing = mcp_server.handle_request(req_missing)
    assert "not found" in resp_missing["result"]["content"][0]["text"]


def test_mcp_call_list_docs_and_sections(mcp_server):
    req_sections = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "jemini_list_sections",
            "arguments": {},
        },
    }
    resp_sections = mcp_server.handle_request(req_sections)
    text = resp_sections["result"]["content"][0]["text"]
    assert "DevDocs" in text
    assert "wiki" in text
    assert "guidelines" in text

    req_list = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": "jemini_list_docs",
            "arguments": {"section": "wiki"},
        },
    }
    resp_list = mcp_server.handle_request(req_list)
    list_text = resp_list["result"]["content"][0]["text"]
    assert "git_flow" in list_text


def test_mcp_unknown_method(mcp_server):
    req = {
        "jsonrpc": "2.0",
        "id": 8,
        "method": "unknown_rpc_method",
    }
    resp = mcp_server.handle_request(req)
    assert "error" in resp
    assert resp["error"]["code"] == -32601
