import json
from pathlib import Path

from fastapi.testclient import TestClient

from opendevmate.api import create_app
from opendevmate.service import Store

ROOT = Path(__file__).resolve().parents[1]


def test_default_language_stays_chinese_and_english_is_opt_in():
    client = TestClient(create_app(Store(":memory:")))
    denied = client.post("/api/projects", json={"name": " ", "description": " "})
    assert denied.status_code == 400
    assert denied.json()["detail"] == "项目名称和说明都不能为空"
    english = client.post(
        "/api/projects",
        json={"name": " ", "description": " "},
        headers={"Accept-Language": "en-US,en;q=0.9"},
    )
    assert english.json()["detail"] == "Project name and description are both required"
    meta = client.get("/api/meta", params={"lang": "en"})
    assert meta.json()["locale"] == "en"
    assert meta.json()["mcp"] == "/mcp"
    assert meta.json()["springAi"] == "streamable-http"
    page = client.get("/dashboard", headers={"Accept-Language": "en"})
    assert "Projects" in page.text
    assert "OpenDevMate" in page.text


def test_mcp_matches_spring_ai_streamable_http():
    client = TestClient(create_app(Store(":memory:")))
    assert client.get("/mcp").status_code == 405
    noted = client.post("/mcp", json={"jsonrpc": "2.0", "method": "notifications/initialized"})
    assert noted.status_code == 202
    init = client.post("/mcp", json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "spring-ai", "version": "1.0.0"}},
    }, headers={"Accept-Language": "en"})
    assert init.json()["result"]["protocolVersion"] == "2025-03-26"
    assert init.json()["result"]["serverInfo"]["name"] == "opendevmate"
    listed = client.post("/mcp", json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, headers={"Accept-Language": "en"})
    names = [item["name"] for item in listed.json()["result"]["tools"]]
    assert "opendevmate_create_project" in names
    assert "external agent" in listed.json()["result"]["tools"][1]["description"].lower() or "No external" in listed.json()["result"]["tools"][1]["description"]
    created = client.post("/mcp", json={
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "opendevmate_create_project", "arguments": {"name": "demo", "description": "local", "locale": "en"}},
    })
    body = created.json()["result"]
    assert body["isError"] is False
    payload = json.loads(body["content"][0]["text"])
    assert payload["name"] == "demo"
    assert "locally" in payload["message"]
    spring = (ROOT / "spring-ai" / "application-mcp.yml").read_text(encoding="utf-8")
    sample = (ROOT / "nacos" / "spring-mcp.yaml").read_text(encoding="utf-8")
    assert "nacos:" in spring
    assert "127.0.0.1" not in spring
    assert "${MCP_SERVICE_URL}" in sample
    assert "127.0.0.1" not in sample
    assert "spring-ai-starter-mcp-client" in (ROOT / "spring-ai" / "pom-snippet.xml").read_text(encoding="utf-8")
