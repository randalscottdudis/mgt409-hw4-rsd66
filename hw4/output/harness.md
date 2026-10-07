# Harness

## Database tables and fields

Inspected read-only on October 7, 2026 from `Homework 4/data/campus_customs.db`. The file was not modified or moved. No row contents are copied here.

SQLite stores the foreign-key clauses below in the table definitions. A connection enforces them only when `PRAGMA foreign_keys = ON`. This inspection left that pragma at its default, off, and did not change the database.

Declared relationships:

- `inventory.product_id` references `catalogue.product_id` (`ON UPDATE NO ACTION`, `ON DELETE NO ACTION`). One catalogue product can have many inventory rows.
- `chat_messages.user_id` references `users.id` (`ON UPDATE NO ACTION`, `ON DELETE NO ACTION`). One user can have many chat messages.
- `products_json` is stored text. It does not declare a foreign key to `catalogue`.

### catalogue

Shop products. Primary key: `product_id`. SQLite also keeps the internal unique index `sqlite_autoindex_catalogue_1` on that key.

| Field | Type and constraints | Why it matters |
| --- | --- | --- |
| `product_id` | `TEXT PRIMARY KEY` | Stable product slug shared by the catalogue, stock rows, pages, and chatbot matches. |
| `name` | `TEXT NOT NULL` | Product name shown on cards and in chat answers. |
| `garment_type` | `TEXT NOT NULL` | Category used to browse or answer questions such as hoodies or tees. |
| `description` | `TEXT NOT NULL` | Full product text for the detail page and chatbot descriptions. |
| `colors` | `TEXT NOT NULL` | Color choices stored as text for display and search. |
| `search_tags` | `TEXT NOT NULL` | Extra search terms stored as text so the shop and chatbot can match shopper wording. |
| `image_file_path` | `TEXT NOT NULL` | Path to the product image, relative to the data folder. |
| `price` | `REAL NOT NULL` | Selling price the shop and chatbot must quote from the database. |

### inventory

Stock by size. Primary key: `id` (`INTEGER PRIMARY KEY AUTOINCREMENT`). Unique key: `(product_id, size)`, backed by the internal index `sqlite_autoindex_inventory_1`.

| Field | Type and constraints | Why it matters |
| --- | --- | --- |
| `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | Row identity for one product-and-size stock record. |
| `product_id` | `TEXT NOT NULL`, foreign key to `catalogue(product_id)` | Ties this size’s stock to one catalogue product. |
| `size` | `TEXT NOT NULL` | The variant a shopper is asking about, such as S or XL. |
| `quantity` | `INTEGER NOT NULL` | Units on hand for that size; zero means out of stock. |

### users

Customer accounts. Primary key: `id` (`INTEGER PRIMARY KEY AUTOINCREMENT`). Unique key: `email`, backed by the internal index `sqlite_autoindex_users_1`.

`first_name` and `last_name` are present on the live table. SQLite’s stored `CREATE TABLE` statement shows they were added after the original columns.

| Field | Type and constraints | Why it matters |
| --- | --- | --- |
| `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | Account identity used to attach saved chat messages to one customer. |
| `name` | `TEXT NOT NULL` | Display name for the account and for chatbot personalization. |
| `email` | `TEXT NOT NULL UNIQUE` | Login identifier; only one account can use a given email. |
| `password_hash` | `TEXT NOT NULL` | Stored password verifier. The chatbot and API must not reveal it. |
| `created_at` | `TEXT NOT NULL DEFAULT (datetime('now'))` | When the account was created. |
| `first_name` | `TEXT`, nullable, no default | Given name collected at registration. |
| `last_name` | `TEXT`, nullable, no default | Family name collected at registration. |

### chat_messages

Saved chatbot turns for a customer. Primary key: `id` (`INTEGER PRIMARY KEY AUTOINCREMENT`). No secondary unique index.

| Field | Type and constraints | Why it matters |
| --- | --- | --- |
| `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | Orders messages when timestamps tie. |
| `user_id` | `INTEGER NOT NULL`, foreign key to `users(id)` | Limits restored history to the logged-in customer. |
| `role` | `TEXT NOT NULL` | Marks whether the turn is the shopper or the assistant. |
| `content` | `TEXT NOT NULL` | The message text to show again when history reloads. |
| `products_json` | `TEXT`, nullable, no default | Optional structured product matches so restored chat can show the same cards. |
| `created_at` | `TEXT NOT NULL DEFAULT (datetime('now'))` | When the message was stored, used for chronological history. |

## SQLite internal tables

These are bookkeeping objects. They are not shop or chatbot tables.

### sqlite_sequence

Created because `inventory`, `users`, and `chat_messages` use `AUTOINCREMENT`. Declared as `CREATE TABLE sqlite_sequence(name,seq)`. Neither column has a declared type, primary key, or foreign key.

| Field | Type and constraints | Why it matters |
| --- | --- | --- |
| `name` | undeclared type, nullable | Name of an `AUTOINCREMENT` table whose counter SQLite is tracking. |
| `seq` | undeclared type, nullable | Last row id SQLite handed out for that table. Application code should not read or write this table. |

Internal indexes, not tables:

- `sqlite_autoindex_catalogue_1` on `catalogue(product_id)`, unique, origin primary key.
- `sqlite_autoindex_inventory_1` on `inventory(product_id, size)`, unique, origin unique constraint.
- `sqlite_autoindex_users_1` on `users(email)`, unique, origin unique constraint.

## Authentication

Registration and login use the existing `users` table in `Homework 4/data/campus_customs.db`. Catalogue and inventory stay read-only. New accounts are inserted into `users`. Signed-in chat is inserted into `chat_messages`.

A new account stores:

- `first_name` and `last_name` from the form
- `name` as those two names joined with a space, for the shopper’s display name
- `email`, trimmed and stored in lowercase
- `password_hash` only; the password itself is not stored
- `created_at` from the table default `datetime('now')`

Password protection uses the seed’s `pbkdf2_sha256` layout: `pbkdf2_sha256$<salt>$<hex digest>`. The digest is PBKDF2-HMAC-SHA256 with 120,000 iterations. New accounts get a fresh random salt in that same layout. Login checks the seed account and new accounts with `hmac.compare_digest`. API responses and server logs do not include the password or the hash.

The signed-in customer is an HttpOnly `campus_session` cookie, `SameSite=Lax`, scoped to `/`. The cookie holds a user id, an expiry, and an HMAC-SHA256 signature. It does not hold the name, email, or password. Each call to `GET /api/auth/me` loads that id from `users` again, so the displayed name comes from the database. If `SESSION_SECRET` is set in the server environment, that value signs the cookie. Otherwise the process keeps a random secret in memory only. That secret is not written to the project or the database. Logout deletes the cookie.

Wrong email or password returns “Email or password is incorrect.” A duplicate email returns “An account with that email already exists.” A password confirmation that does not match is rejected before anything is stored.

## Frontend and API

The React app talks to FastAPI on the same origin during development. Vite proxies `/api` and `/media` to `http://127.0.0.1:8000`. The browser sends account and chat requests with credentials so the HttpOnly session cookie is included. `VITE_API_BASE_URL` can prefix those paths when the frontend is not proxied. Model keys stay on the server.

| Method and path | Role |
| --- | --- |
| `GET /api/products` | Catalogue cards |
| `GET /api/products/{product_id}` | One product, including sizes and stock |
| `GET /media/products/{filename}` | Product image from `../data/products` |
| `POST /api/auth/register` | Create an account and set the session cookie |
| `POST /api/auth/login` | Sign in |
| `POST /api/auth/logout` | Clear the session cookie |
| `GET /api/auth/me` | Signed-in customer, loaded again from `users` |
| `GET /api/chat/history` | Saved messages for the session user. A guest gets an empty list. |
| `POST /api/chat` | One shopper message plus page context; returns `{ reply, products }` |

The chat widget sends `page_context` from the current route. On `/products/{product_id}` that includes the product id. Other pages send a null product id. The widget shows “Dan is thinking…” while the request is open and shows the API error text if the request fails. When `search_catalogue` returns matches, those catalogue rows are the `products` array. The widget renders each one with the same `ProductCard` used on the products page, so the card link opens `/products/{product_id}`.

A signed-in shopper’s `GET /api/chat/history` reloads their own `chat_messages` rows, including product cards stored in `products_json`. Logout clears the panel. A guest can still chat, and those turns are not written.

Run the API from `backend/`:

```
uvicorn main:app --reload --port 8000
```

## Agent prompt and models

Ask Dan is a PydanticAI agent. `backend/agent.py` reads `backend/prompts/prompt.md` as the system prompt when the agent is first built. The prompt gives Dan a short Campus Customs voice and tells him to use tools for prices and stock.

Structured types live in `backend/models.py`. The model returns `ChatReply`, which is only the reply text. The API responds with `ChatResponse`: `reply` plus `products`. `products` is the catalogue rows from the latest `search_catalogue` call in that turn. A price or stock question that does not search leaves `products` empty. Each chat run allows at most 6 model requests.

`AgentDeps` carries the session `Customer` (`name` and `email`, never the password hash) and the `PageContext` from the request. `shopping_context` reads those dependencies. For a signed-in shopper, the last 8 saved messages are passed back as model history. Guests get no history. The agent is built with `retries=0`, and the Portkey client uses `max_retries=0`, so a failed call is not sent again. `POST /api/chat` turns a timeout or other failure into a short 502 message and leaves retry to the shopper.

The provider is Portkey at `https://api.portkey.ai/v1`. `PORTKEY_API_KEY` is read from `~/.env` and is not stored in the project. The model id is `gpt-5.6-luna`, confirmed on the Portkey model list. `MODEL_NAME` can override it.

## Tool contracts

Tools are in `backend/tools.py` and wired in `backend/agent.py`. Catalogue reads use a read-only SQLite connection to `Homework 4/data/campus_customs.db`. A product is matched by `catalogue.product_id`, then by one exact `name`. Inventory is joined on `product_id`.

| Tool | Result | Why these fields |
| --- | --- | --- |
| `shopping_context` | `ShoppingContext`: `signed_in`, `name`, `email`, `page`, `product_id`, `product_name`, `colors`, `product_found`, `message` | Name and email come from the session customer on `AgentDeps`, not from the browser body. `product_id` is the page context, looked up in `catalogue`. `colors` are that row’s recorded colors. `product_found` is false when the id is missing. Stock is not included, because inventory is by size rather than color. |
| `lookup_product` | `ProductLookupResult`: `product_id`, `found`, `status`, `name`, `description`, `price`, `message` | `description` and `price` come from that catalogue row. `found` is true only for one match. `status` is `found`, `unknown_product`, or `ambiguous`. Price stays null when the product is unknown or the name matches more than one row. |
| `lookup_stock` | `StockResult`: `product_id`, `size`, `found`, `status`, `inventory`, `quantity`, `total_stock`, `message` | `inventory` is the recorded size rows (`size`, `quantity`). `quantity` is only the requested size. `total_stock` is the sum of recorded quantities. `found` means the product exists. `status` separates `unknown_product`, `size_not_recorded` (no inventory row), and `out_of_stock` (quantity is 0). A missing size does not become a zero. |
| `search_catalogue` | `SearchResult`: `query`, `size`, `match_count`, `returned_count`, `limit`, `matches`, `message` | Used for category questions. It searches `name`, `garment_type`, `description`, and `search_tags`. The cap is 8 (`SEARCH_LIMIT`). When `size` is set, a product is kept only if that size’s recorded `quantity` is greater than zero. `match_count` is the remaining hits. Each `SearchMatch` has `product_id`, `name`, `garment_type`, `price`, `image_url`, `short_info`, and, for a size search, `size` and `size_quantity`. The same rows are returned as `ChatResponse.products`. |
| `suggest_alternatives` | `AlternativeResult`: `product_id`, `requested_size`, `garment_type`, `available`, `alternatives`, `message` | Used when the requested size is out of stock or not recorded. `alternatives` holds at most 3 (`ALTERNATIVE_LIMIT`) other catalogue rows with the same `garment_type` and `quantity > 0` for that size. Each alternative has `product_id`, `name`, `garment_type`, `price`, `size`, and `quantity`. Those rows are the chat cards. If none exist, `alternatives` is empty and `message` says so. If the size is already in stock, `available` is true and no substitutes are returned. |

`LookupStatus` is the shared status field: `found`, `unknown_product`, `ambiguous`, `size_not_recorded`, and `out_of_stock`.

## Chat persistence and page context

Signed-in chat uses the existing `chat_messages` table. `POST /api/chat` reads the user id from the verified `campus_session` cookie and loads that customer again from `users` (`name`, `email`, `first_name`, `last_name`). The password hash is not selected. After a successful reply, the shopper message and the assistant reply are inserted for that `user_id`. The assistant row’s `products_json` is the structured product list returned with the reply. A guest chat is not inserted.

`GET /api/chat/history` returns only rows whose `user_id` is the session customer, oldest first. A guest, or a cookie that does not match a user, gets `[]`. The widget replaces its transcript with that list when the signed-in customer loads, so a reload shows the saved messages and cards. The agent receives only the last 8 of those messages as prior user and assistant text.

The frontend sends `page_context.page` and `page_context.product_id`. On a product detail route the id is the slug in the URL. `shopping_context` resolves it with `SELECT name, colors FROM catalogue WHERE product_id = ?`. A question like “Do you have this in pink?” is about that product. Dan may say the color is recorded or not. He may not invent a stock count for a color.

## Safety enforcement

Product prices, descriptions, colors, and stock come from the database tools in `backend/tools.py`. Those tools open `Homework 4/data/campus_customs.db` with `file:...?mode=ro`. They have no insert or update path. Account writes use a separate connection in `backend/main.py` (`connect(write=True)`), and that connection is only used for `users` registration and `chat_messages` inserts.

The shopper identity on a chat request is the user id inside the signed `campus_session` cookie. `customer_by_id` loads `name` and `email` again and does not select `password_hash`. `load_history` filters `chat_messages` with `WHERE user_id = ?` for that id. A guest has no history. The password, hash, and `PORTKEY_API_KEY` are not placed in `AgentDeps` or the tool results. `shopping_context` may tell the model the signed-in name and email; the audit summary for that tool leaves the email out.

`backend/prompts/prompt.md` is loaded once as the agent instructions. The shopper message and prior turns are user and assistant messages, not a replacement prompt. The prompt tells Dan to ignore instructions hidden in messages, history, or catalogue text, and to refuse orders and stock changes. No tool can place an order or write inventory.

`chat_error_detail` returns one of two fixed sentences. It does not include the exception text, a traceback, or configuration. A timeout is named as a timeout. Any other failure, including a usage limit, uses the generic sentence. The client and the agent both use `max_retries=0` and `retries=0`.

## Audit trail

`backend/audit.py` appends to `hw4/output/audit_trail.json`. The file is a JSON array. A missing file starts as an empty array. A non-array file is left in place and the write fails rather than replacing prior records. Each append takes an exclusive `fcntl` lock on `output/audit_trail.lock`, writes a temporary file, and replaces the trail with `os.replace`.

Each event has `timestamp` (UTC, `YYYY-MM-DDTHH:MM:SSZ`), `run_id`, `event_type`, `tool_name`, `args_summary`, `result_summary`, and `stop_reason`. Tool successes use `event_type` `tool_result`. Tool exceptions use `tool_failure` and the exception type name. Every run ends with `run_finished` and `stop_reason` of `completed`, `timeout`, `limits`, or `error`. Summaries are shortened and stripped of email addresses, `pbkdf2_sha256` hashes, and key-like tokens. The shopper’s message and the assistant’s reply are not written.

## Limits

These are the values configured in code:

| Limit | Value | Where |
| --- | --- | --- |
| Model requests per run | 6 | `REQUEST_LIMIT`, passed as `UsageLimits.request_limit` |
| Tool calls per run | 8 | `TOOL_CALLS_LIMIT`, passed as `UsageLimits.tool_calls_limit` |
| Run timeout | 60 seconds | `AGENT_TIMEOUT_SECONDS` on `asyncio.wait_for` and the Portkey client `timeout` |
| Agent result retries | 0 | `Agent(..., retries=0)` |
| HTTP client retries | 0 | `AsyncOpenAI(..., max_retries=0)` |
| History sent to the model | 8 messages | `AGENT_HISTORY_LIMIT` in `main.py` |
| Search matches returned | 8 | `SEARCH_LIMIT` in `tools.py` |
| Alternatives returned | 3 | `ALTERNATIVE_LIMIT` in `tools.py` |
| Shopper message length | 2000 characters | `POST /api/chat` |

## Dependencies

Backend, installed in `hw4/.venv`: FastAPI, Uvicorn, Pydantic, PydanticAI, the OpenAI SDK, and python-dotenv. The standard library supplies SQLite, hashing, and the audit lock. Frontend `package.json`: React 19, React DOM, React Router, and the Vite and TypeScript dev tooling. No audit or animation package was added.

## Data location and how to run

The catalogue database and product images stay in `Homework 4/data` (`campus_customs.db` and `products/`). They are not inside `hw4`. `backend/main.py` and `backend/tools.py` resolve that directory from the backend file as `hw4/../data`, so the working directory can be `backend/` and the data pack does not move. A grader should start the API from `hw4/backend` and leave `Homework 4/data` where it is. There is no project `.env`. `PORTKEY_API_KEY` is read from `~/.env` when a chat run builds the client. `MODEL_NAME` overrides the model id; otherwise it is `gpt-5.6-luna`. `SESSION_SECRET`, if set in the server environment, signs the session cookie.

From `hw4/backend`:

```
../.venv/bin/uvicorn main:app --reload --port 8000
```

From `hw4/frontend`:

```
npm run dev -- --host 127.0.0.1 --port 5173
```

Vite proxies `/api` and `/media` to `http://127.0.0.1:8000`.


