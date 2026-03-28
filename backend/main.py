import uvicorn
import os

from seem.api import create_app

if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("BACKEND_PORT", 8000))
    host = os.getenv("BACKEND_HOST", "127.0.0.1")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
    )
