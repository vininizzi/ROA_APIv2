import os
import json
import httpx
from typing import List, Dict, Any, Optional

# Base directory for mock data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MOCK_DATA_DIR = os.path.join(BASE_DIR, "mock_data")

class CanvasAPIClient:
    """
    Client for interacting with the Canvas LMS API or a mock layer offline.
    """
    def __init__(self):
        self.use_mock = os.getenv("USE_CANVAS_MOCK", "true").lower() == "true"
        self.api_url = os.getenv("CANVAS_API_URL", "https://canvas.instructure.com/api/v1")
        self.api_key = os.getenv("CANVAS_API_KEY", "")

    def _read_mock_file(self, filename: str) -> Any:
        try:
            with open(os.path.join(MOCK_DATA_DIR, filename), "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Any:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
        url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        with httpx.Client() as client:
            response = client.request(method, url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()

    def get_courses(self) -> List[Dict[str, Any]]:
        """GET /api/v1/courses"""
        if self.use_mock:
            return self._read_mock_file("courses.json")
        return self._make_request("GET", "/courses")

    def get_course(self, course_id: int) -> Optional[Dict[str, Any]]:
        """GET /api/v1/courses/{course_id}"""
        if self.use_mock:
            courses = self._read_mock_file("courses.json")
            for course in courses:
                if course.get("id") == course_id:
                    return course
            return None
        return self._make_request("GET", f"/courses/{course_id}")

    def get_assignments(self, course_id: int) -> List[Dict[str, Any]]:
        """GET /api/v1/courses/{course_id}/assignments"""
        if self.use_mock:
            assignments = self._read_mock_file("assignments.json")
            return [a for a in assignments if a.get("course_id") == course_id]
        return self._make_request("GET", f"/courses/{course_id}/assignments")

    def get_students(self, course_id: int) -> List[Dict[str, Any]]:
        """GET /api/v1/courses/{course_id}/students"""
        # Currently, the mock students dataset is shared across courses for simplicity.
        # In a real scenario, there might be a mapping table. We just return all students here
        # or filter based on mock logic if needed.
        if self.use_mock:
            return self._read_mock_file("students.json")
        return self._make_request("GET", f"/courses/{course_id}/students")

    def get_user_self(self) -> Dict[str, Any]:
        """GET /api/v1/users/self"""
        if self.use_mock:
            return self._read_mock_file("users.json")
        return self._make_request("GET", "/users/self")

# Instantiate a default client instance
canvas_client = CanvasAPIClient()
