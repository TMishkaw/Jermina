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


def test_api_queue_endpoints():
    enqueue_res = client.post(
        "/queue/enqueue",
        json={
            "channel_id": "test_ai_frontier",
            "topic": "Quantum Computing 2026",
            "metadata": {"source": "unit_test"},
        },
    )
    assert enqueue_res.status_code == 200
    data = enqueue_res.json()
    assert data["status"] == "enqueued"
    assert data["task"]["topic"] == "Quantum Computing 2026"

    list_res = client.get("/queue/tasks?channel_id=test_ai_frontier")
    assert list_res.status_code == 200
    tasks = list_res.json()["tasks"]
    assert any(t["topic"] == "Quantum Computing 2026" for t in tasks)


def test_api_motions_endpoints():
    list_res = client.get("/motions")
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["total_presets"] > 0
    assert any(p["animation"] == "stop" for p in data["presets"])

    get_res = client.get("/motions/stop")
    assert get_res.status_code == 200
    stop_preset = get_res.json()
    assert stop_preset["animation"] == "stop"
    assert "stop_sign" in stop_preset["prop"]

    # 404 for unknown preset
    missing_res = client.get("/motions/unknown_non_existent_preset_xyz")
    assert missing_res.status_code == 404


def test_api_youtube_categories_endpoints():
    cats_res = client.get("/youtube/categories")
    assert cats_res.status_code == 200
    cats = cats_res.json()["categories"]
    assert len(cats) >= 17
    assert any(c["id"] == "28" for c in cats)

    rec_res = client.post(
        "/youtube/categories/recommend",
        json={
            "topic": "Як штучний інтелект Gemini 3.8 програмує",
            "script_text": "Огляд нових можливостей AI моделей",
            "tags": ["#AI", "#Python", "#Gemini"],
        },
    )
    assert rec_res.status_code == 200
    rec = rec_res.json()
    assert rec["category_id"] == "28"
    assert "Science & Technology" in rec["category_name"]


def test_api_endpoints_reflection():
    ep_res = client.get("/api/endpoints")
    assert ep_res.status_code == 200
    data = ep_res.json()
    assert data["total_endpoints"] >= 10
    paths = [e["path"] for e in data["endpoints"]]
    assert "/health" in paths
    assert "/rotator/status" in paths
    assert "/motions" in paths
    assert "/queue/tasks" in paths
    assert "/youtube/categories" in paths

