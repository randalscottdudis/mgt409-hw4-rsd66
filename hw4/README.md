# Campus Customs (Homework 4)

Yale Bulldog Blue storefront with an Ask Dan chatbot. The React app talks to a FastAPI backend. Product facts come from the supplied SQLite catalogue.

## Layout

This repository keeps the project in a folder named `hw4/`. The supplied data pack is not in Git. Place it beside that folder, not inside it:

```
parent/
  hw4/          this project
  data/
    campus_customs.db
    products/   catalogue images
```

`backend/main.py` and `backend/tools.py` resolve that directory from the backend file as `hw4/../data`. The working directory can be `hw4/backend`, and the database does not move. Product images are served from `data/products` at `/media`. The database file itself is not served.

A fresh clone of this repository is the `parent` directory above. Unzip the course data pack so `data/campus_customs.db` and `data/products/` sit next to `hw4/`.

## Python dependencies

From `hw4/`, create a virtual environment and install the pinned backend packages:

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

`requirements.txt` records the versions used for this submission:

- fastapi 0.142.2
- uvicorn 0.54.0
- pydantic 2.13.5
- pydantic-ai 2.54.0
- openai 3.26.0
- python-dotenv 1.2.4

Password hashing uses the Python standard library (`hashlib.pbkdf2_hmac`). SQLite uses the standard library `sqlite3`. Frontend packages are in `frontend/package.json` and `frontend/package-lock.json`.

## Model configuration

Ask Dan uses PydanticAI with the OpenAI Responses API through Portkey at `https://api.portkey.ai/v1`. The model id is `gpt-5.6-luna`. Set `MODEL_NAME` in the environment to override it.

The backend loads `PORTKEY_API_KEY` from `~/.env` when a chat run builds the client. It does not read a project `.env`. `hw4/.env.example` lists placeholder names only. Put the real key in `~/.env`:

```
PORTKEY_API_KEY=your_portkey_api_key
```

`SESSION_SECRET`, if set in the server process environment, signs the `campus_session` cookie. If it is unset, the process uses a random secret that changes on restart.

## Run

Terminal 1, from `hw4/backend`:

```
../.venv/bin/uvicorn main:app --reload --port 8000
```

Terminal 2, from `hw4/frontend`:

```
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open `http://127.0.0.1:5173`. Vite proxies `/api` and `/media` to `http://127.0.0.1:8000`, so the default frontend leaves `VITE_API_BASE_URL` empty and sends cookies with `credentials: "include"`. The API allows credentialed requests from `http://127.0.0.1:5173` and `http://localhost:5173`.

## App-check evidence

Open `hw4/output/app_check.html` in a browser. Screenshot paths are relative to that file (`app_check_images/`). Further notes are in `output/harness.md`, `output/design.md`, and `output/usability.md`.
