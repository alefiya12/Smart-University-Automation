from pydantic import BaseModel
class StudentUpdate(BaseModel):
    full_name: str
    email: str
    department_id: int
    course_id: int
    semester: int
