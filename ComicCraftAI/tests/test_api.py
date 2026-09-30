from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_homepage():

    response = client.get("/")

    assert response.status_code == 200

    assert "ComicCraft" in response.text


def test_json_generation():

    response = client.post(
        "/generate-comic/json",
        json={
            "story_prompt": (
                "A brave fox explores "
                "an enchanted forest."
            ),

            "character_name": "Fenn",

            "setting": "forest",

            "tone": "funny",

            "art_style": "comic book"
        }
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert len(body["layout"]) == 5

    assert body["pdf_url"].endswith(
        ".pdf"
    )