from langchain.tools import tool
from services.canvas_mock_api import canvas_client
from typing import List, Dict, Any, Optional

@tool
def get_canvas_courses() -> List[Dict[str, Any]]:
    """
    Get the list of all available courses in Canvas. 
    Use this to find course IDs and names.
    """
    return canvas_client.get_courses()

@tool
def get_canvas_course_details(course_id: int) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific Canvas course by its ID.
    """
    return canvas_client.get_course(course_id)

@tool
def get_canvas_assignments(course_id: int) -> List[Dict[str, Any]]:
    """
    Get the list of assignments for a specific Canvas course ID.
    """
    return canvas_client.get_assignments(course_id)

@tool
def get_canvas_students(course_id: int) -> List[Dict[str, Any]]:
    """
    Get the list of students enrolled in a specific Canvas course ID.
    """
    return canvas_client.get_students(course_id)

@tool
def get_canvas_user_me() -> Dict[str, Any]:
    """
    Get information about the currently authenticated user in Canvas.
    """
    return canvas_client.get_user_self()

# List of all tools to be exported
canvas_tools = [
    get_canvas_courses,
    get_canvas_course_details,
    get_canvas_assignments,
    get_canvas_students,
    get_canvas_user_me
]
