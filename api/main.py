from fastapi import FastAPI
from routes import employee_routes, text_routes, document_generator_routes, index_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # Replace this value with the IP whitelist in production
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

### employee_routes exposes 2 endpoints:
# api/employees
# api/employees/{id} 
app.include_router(employee_routes.router, prefix="/api")
app.include_router(text_routes.router, prefix="/api")
app.include_router(document_generator_routes.router, prefix="/api")
app.include_router(index_routes.router, prefix="/api")