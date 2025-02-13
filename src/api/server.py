"""
Script to run the Scene+ recommendation API server.
"""
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from environment
HOST = os.getenv("API_HOST", "0.0.0.0")
PORT = int(os.getenv("API_PORT", "8000"))
DEBUG = os.getenv("API_DEBUG", "False").lower() == "true"
WORKERS = int(os.getenv("API_WORKERS", "1"))

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "endpoints:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        workers=WORKERS,
        log_level="info" if DEBUG else "warning"
    ) 