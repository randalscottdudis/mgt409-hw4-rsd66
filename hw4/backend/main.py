"""Products, images, and account API for the Campus Customs storefront.

Paths are resolved from this file so `uvicorn main:app` works when the
working directory is backend/. The database and images stay in
../data relative to hw4/. Catalogue reads are read-only. Account
registration inserts into users. Signed-in chat inserts into chat_messages.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pydantic import ValidationError

from agent import prior_messages, run_chat
from models import (
    ChatHistoryMessage,
    ChatRequest,
    ChatResponse,
    Customer,
    InventoryItem,
    LoginRequest,
    Product,
    RegisterRequest,
)

BACKEND_DIR = Path(__file__).resolve().parent
HW4_DIR = BACKEND_DIR.parent
DATA_DIR = (HW4_DIR / ".." / "data").resolve()
DATABASE_PATH = DATA_DIR / "campus_customs.db"
PRODUCTS_DIR = DATA_DIR / "products"

SIZE_ORDER = {"XS": 0, "S": 1, "M": 2, "L": 3, "XL": 4, "XXL": 5}
HASH_SCHEME = "pbkdf2_sha256"
HASH_ITERATIONS = 120_000
SESSION_COOKIE = "campus_session"
SESSION_MAX_AGE = 60 * 60 * 12
AGENT_HISTORY_LIMIT = 8
_PROCESS_SESSION_SECRET = secrets.token_bytes(32)


def image_filename(image_file_path: str) -> str:
    path = Path(image_file_path)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe image path: {image_file_path}")
    if path.as_posix() != f"products/{path.name}" or not path.name:
        raise ValueError(f"Unexpected image path: {image_file_path}")
    return path.name


def string_list(raw: str) -> list[str]:
    parsed = json.loads(raw)
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise ValueError("Expected a JSON list of strings")
    return parsed


def to_product(row: sqlite3.Row, inventory: list[InventoryItem]) -> Product:
    filename = image_filename(row["image_file_path"])
    ordered = sorted(inventory, key=lambda item: (SIZE_ORDER.get(item.size, 100), item.size))
    return Product(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        image_file_path=row["image_file_path"],
        image_url=f"/media/products/{filename}",
        colors=string_list(row["colors"]),
        search_tags=string_list(row["search_tags"]),
        price=float(row["price"]),
        inventory=ordered,
        total_stock=sum(item.quantity for item in ordered),
    )


@contextmanager
def connect(*, write: bool = False) -> Iterator[sqlite3.Connection]:
    if not DATABASE_PATH.is_file():
        raise FileNotFoundError(f"Database not found: {DATABASE_PATH}")
    if write:
        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return
    connection = sqlite3.connect(f"file:{DATABASE_PATH}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    connection.isolation_level = None
    try:
        yield connection
    finally:
        connection.close()


def hash_password(password: str) -> str:
    salt = secrets.token_urlsafe(12)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), HASH_ITERATIONS)
    return f"{HASH_SCHEME}${salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    scheme, separator, remainder = stored.partition("$")
    salt, separator, digest = remainder.partition("$")
    if scheme != HASH_SCHEME or not separator or not salt or not digest:
        return False
    calculated = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), HASH_ITERATIONS)
    return hmac.compare_digest(calculated.hex(), digest)


_DUMMY_PASSWORD_HASH = hash_password(secrets.token_urlsafe(16))


def session_secret() -> bytes:
    configured = os.environ.get("SESSION_SECRET", "").strip()
    if configured:
        return configured.encode()
    return _PROCESS_SESSION_SECRET


def write_session(response: Response, user_id: int) -> None:
    expires = int(time.time()) + SESSION_MAX_AGE
    payload = f"{user_id}.{expires}".encode()
    signature = hmac.new(session_secret(), payload, hashlib.sha256).hexdigest()
    response.set_cookie(
        key=SESSION_COOKIE,
        value=f"{payload.decode()}.{signature}",
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )


def read_session(request: Request) -> int | None:
    token = request.cookies.get(SESSION_COOKIE, "")
    user_id, expires, signature = (token.split(".") + ["", "", ""])[:3]
    if not user_id or not expires or not signature:
        return None
    payload = f"{user_id}.{expires}".encode()
    expected = hmac.new(session_secret(), payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return None
    try:
        if int(expires) < time.time():
            return None
        return int(user_id)
    except ValueError:
        return None


def clean_person_name(value: str, label: str) -> str:
    cleaned = " ".join(value.split())
    if not cleaned:
        raise HTTPException(status_code=400, detail=f"Enter a {label}.")
    if len(cleaned) > 80:
        raise HTTPException(status_code=400, detail=f"That {label} is too long.")
    return cleaned


def clean_email(value: str) -> str:
    email = value.strip().lower()
    if "@" not in email or email.startswith("@") or email.endswith("@") or " " in email:
        raise HTTPException(status_code=400, detail="Enter a valid email address.")
    return email


def customer_from_row(row: sqlite3.Row) -> Customer:
    return Customer(
        user_id=int(row["id"]),
        name=row["name"],
        email=row["email"],
        first_name=row["first_name"],
        last_name=row["last_name"],
    )


def customer_by_id(user_id: int) -> Customer | None:
    with connect() as connection:
        row = connection.execute(
            """
            SELECT id, name, email, first_name, last_name
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()
        if row is None:
            return None
        return customer_from_row(row)


def products_from_json(raw: str | None) -> list[Product]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    products: list[Product] = []
    for item in parsed:
        try:
            products.append(Product.model_validate(item))
        except ValidationError:
            continue
    return products


def load_history(user_id: int) -> list[ChatHistoryMessage]:
    """Messages for this user id only. The id comes from the verified session."""
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT id, role, content, products_json, created_at
            FROM chat_messages
            WHERE user_id = ?
            ORDER BY id
            """,
            (user_id,),
        ).fetchall()
    messages: list[ChatHistoryMessage] = []
    for row in rows:
        if row["role"] not in {"user", "assistant"}:
            continue
        messages.append(
            ChatHistoryMessage(
                id=int(row["id"]),
                role=row["role"],
                content=row["content"],
                products=products_from_json(row["products_json"]),
                created_at=row["created_at"],
            )
        )
    return messages


def save_exchange(user_id: int, user_message: str, reply: str, products: list[Product]) -> None:
    """Store one shopper message and the assistant reply for that same user id."""
    products_json = json.dumps([product.model_dump() for product in products])
    with connect(write=True) as connection:
        connection.execute(
            """
            INSERT INTO chat_messages (user_id, role, content, products_json)
            VALUES (?, 'user', ?, NULL)
            """,
            (user_id, user_message),
        )
        connection.execute(
            """
            INSERT INTO chat_messages (user_id, role, content, products_json)
            VALUES (?, 'assistant', ?, ?)
            """,
            (user_id, reply, products_json),
        )


def chat_error_detail(exc: Exception) -> str:
    """Shopper-facing failure text. The server does not call the model again."""
    if isinstance(exc, TimeoutError) or "Timeout" in type(exc).__name__:
        return "Ask Dan timed out before answering. Nothing was retried. Use Retry to ask again."
    return "Ask Dan could not answer. Nothing was retried automatically. Use Retry to ask again."


def inventory_by_product(connection: sqlite3.Connection) -> dict[str, list[InventoryItem]]:
    grouped: dict[str, list[InventoryItem]] = {}
    rows = connection.execute("SELECT product_id, size, quantity FROM inventory")
    for row in rows:
        grouped.setdefault(row["product_id"], []).append(
            InventoryItem(size=row["size"], quantity=int(row["quantity"]))
        )
    return grouped


app = FastAPI(title="Campus Customs")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.post("/api/auth/register", response_model=Customer)
def register(body: RegisterRequest, response: Response) -> Customer:
    first_name = clean_person_name(body.first_name, "first name")
    last_name = clean_person_name(body.last_name, "last name")
    email = clean_email(body.email)
    if body.password != body.password_confirmation:
        raise HTTPException(status_code=400, detail="Password confirmation does not match.")
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Use at least 8 characters for the password.")
    password_hash = hash_password(body.password)
    display_name = f"{first_name} {last_name}"
    try:
        with connect(write=True) as connection:
            cursor = connection.execute(
                """
                INSERT INTO users (name, email, password_hash, first_name, last_name)
                VALUES (?, ?, ?, ?, ?)
                """,
                (display_name, email, password_hash, first_name, last_name),
            )
            user_id = int(cursor.lastrowid)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="An account with that email already exists.") from None
    write_session(response, user_id)
    created = customer_by_id(user_id)
    if created is None:
        raise HTTPException(status_code=500, detail="The account was created but could not be loaded.")
    return created


@app.post("/api/auth/login", response_model=Customer)
def login(body: LoginRequest, response: Response) -> Customer:
    email = clean_email(body.email)
    with connect() as connection:
        row = connection.execute(
            """
            SELECT id, name, email, first_name, last_name, password_hash
            FROM users
            WHERE email = ?
            """,
            (email,),
        ).fetchone()
        stored_hash = row["password_hash"] if row else _DUMMY_PASSWORD_HASH
        customer = customer_from_row(row) if row else None
    if customer is None or not verify_password(body.password, stored_hash):
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")
    write_session(response, customer.user_id)
    return customer


@app.post("/api/auth/logout", status_code=204)
def logout(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE, path="/", httponly=True, samesite="lax", secure=False)


@app.get("/api/auth/me", response_model=Customer)
def me(request: Request) -> Customer:
    user_id = read_session(request)
    customer = customer_by_id(user_id) if user_id is not None else None
    if customer is None:
        raise HTTPException(status_code=401, detail="Sign in to continue.")
    return customer


@app.get("/api/chat/history", response_model=list[ChatHistoryMessage])
def chat_history(request: Request) -> list[ChatHistoryMessage]:
    user_id = read_session(request)
    customer = customer_by_id(user_id) if user_id is not None else None
    if customer is None:
        return []
    return load_history(customer.user_id)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, request: Request) -> ChatResponse:
    message = " ".join(body.message.split())
    if not message:
        raise HTTPException(status_code=400, detail="Enter a message.")
    if len(message) > 2000:
        raise HTTPException(status_code=400, detail="That message is too long.")
    user_id = read_session(request)
    customer = customer_by_id(user_id) if user_id is not None else None
    history = load_history(customer.user_id) if customer else []
    recent = [(item.role, item.content) for item in history[-AGENT_HISTORY_LIMIT:]]
    try:
        response = await run_chat(message, body.page_context, customer, prior_messages(recent))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=chat_error_detail(exc)) from exc
    if customer is not None:
        save_exchange(customer.user_id, message, response.reply, response.products)
    return response


@app.get("/api/products", response_model=list[Product])
def list_products() -> list[Product]:
    with connect() as connection:
        inventory = inventory_by_product(connection)
        rows = connection.execute(
            """
            SELECT product_id, name, garment_type, description, colors,
                   search_tags, image_file_path, price
            FROM catalogue
            ORDER BY name COLLATE NOCASE, product_id
            """
        )
        return [to_product(row, inventory.get(row["product_id"], [])) for row in rows]


@app.get("/api/products/{product_id}", response_model=Product)
def get_product(product_id: str) -> Product:
    with connect() as connection:
        row = connection.execute(
            """
            SELECT product_id, name, garment_type, description, colors,
                   search_tags, image_file_path, price
            FROM catalogue
            WHERE product_id = ?
            """,
            (product_id,),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="No catalogue product matches that id.")
        items = connection.execute(
            """
            SELECT size, quantity
            FROM inventory
            WHERE product_id = ?
            """,
            (product_id,),
        ).fetchall()
    inventory = [InventoryItem(size=item["size"], quantity=int(item["quantity"])) for item in items]
    return to_product(row, inventory)


if not PRODUCTS_DIR.is_dir():
    raise RuntimeError(f"Product image directory not found: {PRODUCTS_DIR}")

app.mount("/media/products", StaticFiles(directory=PRODUCTS_DIR), name="product-images")
