from fastapi.testclient import TestClient
from jobmatch.main import app

client = TestClient(app)


def test_ranks_the_closest_job():
    payload = client.post("/match", json={"resume": 'kubernetes terraform oncall sre'}).json()
    assert payload["matches"][0]["job"] == "platform"
