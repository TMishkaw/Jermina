from fastapi.testclient import TestClient

from jemini.api.app import app

client = TestClient(app)


def test_api_root_and_docs():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["engine"] == "Jemini Core"
    assert data["status"] == "operational"
    assert data["docs"] == "/docs"
    assert data["wiki"] == "/wiki"

    # Swagger /docs
    docs_res = client.get("/docs")
    assert docs_res.status_code == 200


def test_api_wiki():
    wiki_res = client.get("/wiki")
    assert wiki_res.status_code == 200
    assert "Jemini Autonomous Wiki" in wiki_res.text
    assert "Key Rotator & Quota Manager" in wiki_res.text


def test_api_rotator_endpoints():
    status_res = client.get("/rotator/status")
    assert status_res.status_code == 200
    assert "keys" in status_res.json()

    reg_res = client.post(
        "/rotator/keys",
        json={
            "api_key": "api_test_mock_key_999",
            "engine": "gemini",
            "key_type": "free",
        },
    )
    assert reg_res.status_code == 200
    assert "Key registered" in reg_res.json()["message"]


def test_api_channel_onboarding():
    onboard_payload = {
        "channel_id": "test_ai_frontier",
        "channel_name": "AI Frontier Channel",
        "core_theme": "Quantum computing & LLMs",
        "accent_color": "#FF00AA",
        "voice_name": "Fenrir",
        "default_tags": ["#AI", "#Quantum", "#Shorts"],
    }
    post_res = client.post("/channels/onboard", json=onboard_payload)
    assert post_res.status_code == 200
    assert post_res.json()["status"] == "success"

    list_res = client.get("/channels")
    assert list_res.status_code == 200
    ch_ids = [c["channel_id"] for c in list_res.json()["channels"]]
    assert "test_ai_frontier" in ch_ids
