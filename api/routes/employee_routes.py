from fastapi import APIRouter, HTTPException
from models.employee import EmployeeGetResponse
from services.employee_service import get_all_employees, get_employee_by_id
from typing import List

router = APIRouter()

@router.get("/employees", response_model=List[EmployeeGetResponse])
async def fetch_employees():
    return get_all_employees()

@router.get("/employees/{employee_id}", response_model=EmployeeGetResponse)
async def fetch_employee_by_id(employee_id):
    employee = get_employee_by_id(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee