import hashlib

from fastapi import FastAPI, HTTPException

app = FastAPI()

# Demo users. Passwords are stored as SHA-256 hashes, never as plain text.
users_db = {
    "demo": hashlib.sha256("demo123".encode()).hexdigest(),
}


# GET - log in with username and password
# Note: sending a password in the URL is not secure; POST is the usual choice for login.
@app.get("/login")
def login(username: str, password: str):
    stored_hash = users_db.get(username)
    given_hash = hashlib.sha256(password.encode()).hexdigest()
    if stored_hash is None or stored_hash != given_hash:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": f"Welcome, {username}!", "username": username}
