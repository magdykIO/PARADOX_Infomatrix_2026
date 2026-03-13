

# Create the database tables, look in "models.py"
# models.Base.metadata.create_all(bind=engine)


# Exeption handler for unknown pages
@app.exception_handler(404)
async def custom_404_handler(request: Request, __):
    return FileResponse("templates/404.html")


# Starts up the server on running "main.py" file
if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database is ready. Starting the messenger...")

    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
