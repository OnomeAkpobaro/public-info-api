from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import uvicorn
from config import Config


app = FastAPI(
    title=Config.API_TITLE,
    description=Config.API_DESCRIPTION,
    version=Config.API_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def get_info():
    """
    Returns basic informaton including email, current datetime, and GitHub URL
    """

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "email": Config.EMAIL,
            "current_datetime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "github_url": Config.GITHUB_URL,
        }
    )

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify if the API is running
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    # Run the FastAPI app using uvicorn
    uvicorn.run("main:app", host=Config.HOST, port=Config.PORT, reload=Config.DEBUG)
