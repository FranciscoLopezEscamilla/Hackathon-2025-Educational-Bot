from fastapi import FastAPI
from routes import employee_routes, text_routes, image_routes, index_routes

app = FastAPI()

### employee_routes exposes 2 endpoints:
# api/employees
# api/employees/{id} 
app.include_router(employee_routes.router, prefix="/api")
app.include_router(text_routes.router, prefix="/api")
app.include_router(image_routes.router, prefix="/api")
app.include_router(index_routes.router, prefix="/api")