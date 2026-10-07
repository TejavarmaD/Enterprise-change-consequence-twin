from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_change_routes_are_registered():
    paths = set(app.openapi()["paths"])

    assert "/changes" in paths
    assert "/changes/{change_id}" in paths


def test_consequence_routes_are_registered():
    paths = set(app.openapi()["paths"])

    assert "/changes/{change_id}/consequences" in paths
    assert "/changes/{change_id}/consequences/{consequence_id}" in paths