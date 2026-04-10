from fastapi import FastAPI

from api.routes import user

app = FastAPI()

app.include_router(user.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
