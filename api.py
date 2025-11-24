
if __name__ == "__main__":
    # Run the FastAPI app with Uvicorn on port 9090
    try:
        import uvicorn
    except Exception:
        raise RuntimeError("uvicorn is required to run the server. Install with `pip install uvicorn`.")

    uvicorn.run("cmd.rest_api.main:app", host="0.0.0.0", port=9090, log_level="info")
