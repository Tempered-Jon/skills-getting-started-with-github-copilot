from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import activities


def test_get_activities_returns_full_activity_list(client: TestClient):
    # Arrange
    sample_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert sample_activity in response_json
    assert response_json[sample_activity]["description"] == activities[sample_activity]["description"]
    assert "participants" in response_json[sample_activity]


def test_signup_for_activity_adds_participant(client: TestClient):
    # Arrange
    activity_name = "Basketball Team"
    email = "newstudent@mergington.edu"
    assert email not in activities[activity_name]["participants"]

    # Act
    response = client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email)}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]
    assert email in client.get("/activities").json()[activity_name]["participants"]


def test_signup_duplicate_returns_400(client: TestClient):
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email)}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_student(client: TestClient):
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    # Act
    response = client.delete(f"/activities/{quote(activity_name)}/participants/{quote(email, safe='')}" )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_nonexistent_participant_returns_404(client: TestClient):
    # Arrange
    activity_name = "Basketball Team"
    email = "fakeuser@mergington.edu"

    # Act
    response = client.delete(f"/activities/{quote(activity_name)}/participants/{quote(email, safe='')}" )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
