from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import init_db
from routers.router_handler import router_handler


# Initializing app and toggling on router files
app = FastAPI()
app.include_router(router_handler)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Starts up the server on running "main.py" file
if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database is ready. Starting the messenger...")

    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
