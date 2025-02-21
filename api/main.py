from fastapi import FastAPI
from routes import employee_routes

app = FastAPI()

### employee_routes exposes 2 endpoints:
# api/employees
# api/employees/{id} 
app.include_router(employee_routes.router, prefix="/api")