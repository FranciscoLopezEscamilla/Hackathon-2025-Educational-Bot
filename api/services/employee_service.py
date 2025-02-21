from models.employee import EmployeeGetResponse
from typing import List

# lets simulate an in-memory database
employees = [
    {
        "id": 1,
        "name": "Pedro"
    },
    {
        "id": 2,
        "name": "Francisco"
    },
    {
        "id": 3,
        "name": "Daniel"
    }
]

# this service simulates an operation that returns a collection of Employees
def get_all_employees() -> List[EmployeeGetResponse]:
    return employees

# this service simulates an operation that returns an Employee object based on the ID
def get_employee_by_id(employee_id: int) -> EmployeeGetResponse:
    for emp in employees:
        if emp["id"] == int(employee_id):
            return emp
    return None