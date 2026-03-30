"""
Integration tests for Mergington High School API endpoints
Tests follow the AAA (Arrange-Act-Assert) pattern for clarity
"""
import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """
        ARRANGE: Setup test client
        ACT: Make GET request to root endpoint
        ASSERT: Verify redirect to static index.html
        """
        # ARRANGE
        expected_url = "/static/index.html"
        
        # ACT
        response = client.get("/", follow_redirects=False)
        
        # ASSERT
        assert response.status_code == 307
        assert expected_url in response.headers["location"]


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_success(self, client):
        """
        ARRANGE: Setup test client
        ACT: Make GET request to /activities endpoint
        ASSERT: Verify response status is 200
        """
        # ARRANGE
        expected_status = 200
        
        # ACT
        response = client.get("/activities")
        
        # ASSERT
        assert response.status_code == expected_status

    def test_get_activities_returns_dict_structure(self, client):
        """
        ARRANGE: Setup test client
        ACT: Make GET request to /activities endpoint
        ASSERT: Verify response is a dictionary with activity names as keys
        """
        # ARRANGE
        # ACT
        response = client.get("/activities")
        data = response.json()
        
        # ASSERT
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_get_activities_includes_required_fields(self, client):
        """
        ARRANGE: Setup test client and expected required fields
        ACT: Make GET request to /activities endpoint
        ASSERT: Verify each activity has required fields
        """
        # ARRANGE
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # ACT
        response = client.get("/activities")
        activities = response.json()
        
        # ASSERT
        assert len(activities) > 0
        for activity_name, activity_details in activities.items():
            assert isinstance(activity_details, dict)
            for field in required_fields:
                assert field in activity_details, f"Activity '{activity_name}' missing field '{field}'"

    def test_get_activities_participants_is_list(self, client):
        """
        ARRANGE: Setup test client
        ACT: Make GET request to /activities endpoint
        ASSERT: Verify participants field is a list
        """
        # ARRANGE
        # ACT
        response = client.get("/activities")
        activities = response.json()
        
        # ASSERT
        for activity_name, activity_details in activities.items():
            assert isinstance(activity_details["participants"], list), \
                f"Activity '{activity_name}' participants should be a list"

    def test_get_activities_has_known_activity(self, client):
        """
        ARRANGE: Setup test client and expected activity name
        ACT: Make GET request to /activities endpoint
        ASSERT: Verify Chess Club activity exists
        """
        # ARRANGE
        expected_activity = "Chess Club"
        
        # ACT
        response = client.get("/activities")
        activities = response.json()
        
        # ASSERT
        assert expected_activity in activities


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful_with_new_email(self, client):
        """
        ARRANGE: Setup test client with new email and valid activity
        ACT: Make POST request to signup endpoint
        ASSERT: Verify response status is 200 with success message
        """
        # ARRANGE
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """
        ARRANGE: Setup test client with new email and valid activity
        ACT: Make POST request to signup endpoint
        ASSERT: Verify participant was added by checking activities endpoint
        """
        # ARRANGE
        email = "addedstudent@mergington.edu"
        activity_name = "Programming Class"
        
        # ACT - Sign up
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ACT - Check activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # ASSERT
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_signup_with_duplicate_email_fails(self, client):
        """
        ARRANGE: Setup test client with existing participant email
        ACT: Make POST request to signup same email for same activity
        ASSERT: Verify response status is 400 with error message
        """
        # ARRANGE
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already signed up for Chess Club
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # ASSERT
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()

    def test_signup_to_nonexistent_activity_fails(self, client):
        """
        ARRANGE: Setup test client with valid email and non-existent activity
        ACT: Make POST request to signup to activity that doesn't exist
        ASSERT: Verify response status is 404 with error message
        """
        # ARRANGE
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_same_email_different_activities(self, client):
        """
        ARRANGE: Setup test client with same email for two different activities
        ACT: Sign up for first activity, then sign up for second activity
        ASSERT: Verify both signups succeed
        """
        # ARRANGE
        email = "multiactivity@mergington.edu"
        activity1 = "Tennis Club"
        activity2 = "Drama Club"
        
        # ACT - Sign up for first activity
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )
        
        # ACT - Sign up for second activity
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_signup_response_structure(self, client):
        """
        ARRANGE: Setup test client with new email and valid activity
        ACT: Make POST request to signup endpoint
        ASSERT: Verify response has correct structure
        """
        # ARRANGE
        email = "structuretest@mergington.edu"
        activity_name = "Science Club"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # ASSERT
        assert response.status_code == 200
        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0
