"""Page For Password Reset login service."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.users import AccountExistsError, InvalidAccountError, UserStore

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="Page For Password Reset")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
store = UserStore()


class Credentials(BaseModel):
    email: str
    password: str


@app.get("/", response_class=HTMLResponse)
def login_page() -> str:
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/register", status_code=201)
def register(body: Credentials) -> dict:
    try:
        user = store.register(body.email, body.password)
    except AccountExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except InvalidAccountError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"email": user.email}


@app.post("/api/login")
def login(body: Credentials) -> dict:
    token = store.authenticate(body.email, body.password)
    if token is None:
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    return {"token": token, "email": store.normalize(body.email)}


@app.get("/api/me")
def me(authorization: str = Header(default="")) -> dict:
    token = authorization.removeprefix("Bearer ").strip()
    email = store.user_for_token(token) if token else None
    if email is None:
        raise HTTPException(status_code=401, detail="Not signed in.")
    return {"email": email}
