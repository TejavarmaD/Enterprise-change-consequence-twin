from backend.app.models import Base


EXPECTED_TABLES = {
    "apis",
    "business_processes",
    "business_rules",
    "changes",
    "consequence_assessments",
    "data_assets",
    "data_pipelines",
    "databases",
    "deployments",
    "documents",
    "incidents",
    "metrics",
    "ml_models",
    "policies",
    "services",
    "systems",
    "teams",
    "tests",
}


def test_all_ecct_models_registered():
    assert set(Base.metadata.tables.keys()) == EXPECTED_TABLES