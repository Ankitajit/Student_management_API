import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from datetime import datetime

from app.database import engine, Base
from app.routers import records, audit

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Enterprise RBAC System",
    description="PostgreSQL Role-Based Application with Database Connectivity.",
    version="2.0.0"
)

# 1. Centralized Exception Handling 
@app.exception_handler(HTTPException)
def global_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status_code": exc.status_code,
            "error_message": exc.detail,
            "api_path": request.url.path,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# 2. Linking Routers
app.include_router(records.router)
app.include_router(audit.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)