from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_openapi_document_is_available():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    document = response.json()

    assert document["info"]["title"] == (
        "Enterprise Change Consequence Twin"
    )


def test_change_error_responses_are_documented():
    document = client.get("/openapi.json").json()

    create_change = document["paths"]["/changes"]["post"]
    get_change = document["paths"]["/changes/{change_id}"]["get"]

    assert "409" in create_change["responses"]
    assert "422" in create_change["responses"]
    assert "404" in get_change["responses"]


def test_consequence_error_responses_are_documented():
    document = client.get("/openapi.json").json()

    create_consequence = document[
        "paths"
    ]["/changes/{change_id}/consequences"]["post"]

    list_consequences = document[
        "paths"
    ]["/changes/{change_id}/consequences"]["get"]

    get_consequence = document[
        "paths"
    ]["/changes/{change_id}/consequences/{consequence_id}"]["get"]

    assert "404" in create_consequence["responses"]
    assert "422" in create_consequence["responses"]

    assert "404" in list_consequences["responses"]
    assert "422" in list_consequences["responses"]

    assert "404" in get_consequence["responses"]


def test_error_response_schema_is_registered():
    document = client.get("/openapi.json").json()

    schemas = document["components"]["schemas"]

    assert "ErrorResponse" in schemas
    assert schemas["ErrorResponse"]["properties"]["detail"]["type"] == "string"
    assert schemas["ErrorResponse"]["required"] == ["detail"]