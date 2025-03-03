from fastapi import FastAPI
import uvicorn
from database import engine, Base
import routes

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include routes
app.include_router(routes.router, prefix="/api", tags=["users"])


if __name__ == "__main__":
    uvicorn.run(app)
