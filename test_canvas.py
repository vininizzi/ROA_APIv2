import sys
import os

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.canvas_mock_api import canvas_client

def test_mock():
    print("Testing Canvas API Mock Client (USE_CANVAS_MOCK defaults to true)")
    print("Courses: ", canvas_client.get_courses())
    print("User Self: ", canvas_client.get_user_self())
    print("Assignments for Course 101: ", canvas_client.get_assignments(101))
    
if __name__ == "__main__":
    test_mock()
