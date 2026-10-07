"""Agent tools. Catalogue and inventory reads stay read-only."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from models import (
    AlternativeResult,
    Customer,
    InventoryItem,
    LookupStatus,
    PageContext,
    Product,
    ProductLookupResult,
    SearchMatch,
    SearchResult,
    ShoppingContext,
    StockAlternative,
    StockResult,
)

BACKEND_DIR = Path(__file__).resolve().parent
DATABASE_PATH = (BACKEND_DIR.parent / ".." / "data" / "campus_customs.db").resolve()
SEARCH_LIMIT = 8
ALTERNATIVE_LIMIT = 3
SIZE_ORDER = {"XS": 0, "S": 1, "M": 2, "L": 3, "XL": 4, "XXL": 5}
SEARCH_STOPWORDS = {
    "a",
    "an",
    "any",
    "are",
    "do",
    "for",
    "have",
    "is",
    "me",
    "of",
    "show",
    "some",
    "the",
    "there",
    "what",
    "which",
    "you",
    "your",
}
SIZE_ALIASES = {
    "xs": "XS",
    "extra small": "XS",
    "s": "S",
    "small": "S",
    "m": "M",
    "medium": "M",
    "med": "M",
    "l": "L",
    "large": "L",
    "xl": "XL",
    "extra large": "XL",
    "xxl": "XXL",
    "2xl": "XXL",
    "extra extra large": "XXL",
}


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(f"file:{DATABASE_PATH}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    connection.isolation_level = None
    try:
        yield connection
    finally:
        connection.close()


def shopping_context(customer: Customer | None, page_context: PageContext) -> ShoppingContext:
    """Who is here, which page is open, and the catalogue row for that product_id. No stock."""
    product_name = None
    colors: list[str] = []
    product_found = False
    product_id = page_context.product_id
    if product_id:
        with connect() as connection:
            row = connection.execute(
                "SELECT name, colors FROM catalogue WHERE product_id = ?",
                (product_id,),
            ).fetchone()
        if row is None:
            message = "That product_id is not in the catalogue."
        else:
            product_found = True
            product_name = row["name"]
            colors = _string_list(row["colors"])
            listed = ", ".join(colors) if colors else "none"
            message = (
                f"The open product is {product_name} ({product_id}). "
                f"Recorded colors: {listed}. Stock is by size, not by color."
            )
    else:
        message = "No product is open on this page."
    return ShoppingContext(
        signed_in=customer is not None,
        name=customer.name if customer else None,
        email=customer.email if customer else None,
        page=page_context.page,
        product_id=product_id,
        product_name=product_name,
        colors=colors,
        product_found=product_found,
        message=message,
    )


def normalize_size(size: str | None) -> str | None:
    if size is None:
        return None
    cleaned = " ".join(size.strip().lower().split())
    if not cleaned:
        return None
    return SIZE_ALIASES.get(cleaned, size.strip().upper())


def _inventory(connection: sqlite3.Connection, product_id: str) -> list[InventoryItem]:
    rows = connection.execute(
        "SELECT size, quantity FROM inventory WHERE product_id = ?",
        (product_id,),
    )
    items = [InventoryItem(size=row["size"], quantity=int(row["quantity"])) for row in rows]
    items.sort(key=lambda item: (SIZE_ORDER.get(item.size, 100), item.size))
    return items


def _match_product(connection: sqlite3.Connection, product_ref: str) -> tuple[sqlite3.Row | None, list[sqlite3.Row]]:
    ref = product_ref.strip()
    exact = connection.execute(
        """
        SELECT product_id, name, description, price
        FROM catalogue
        WHERE product_id = ?
        """,
        (ref,),
    ).fetchone()
    if exact is not None:
        return exact, []
    named = connection.execute(
        """
        SELECT product_id, name, description, price
        FROM catalogue
        WHERE name = ? COLLATE NOCASE
        ORDER BY product_id
        """,
        (ref,),
    ).fetchall()
    if len(named) == 1:
        return named[0], []
    return None, list(named)


def lookup_product(product_ref: str) -> ProductLookupResult:
    """Name, description, and price for one catalogue product. No guessed values."""
    with connect() as connection:
        row, matches = _match_product(connection, product_ref)
    if matches:
        choices = ", ".join(f"{item['name']} ({item['product_id']})" for item in matches)
        return ProductLookupResult(
            product_id=None,
            found=False,
            status=LookupStatus.ambiguous,
            message=f"More than one product has that name: {choices}.",
        )
    if row is None:
        return ProductLookupResult(
            product_id=None,
            found=False,
            status=LookupStatus.unknown_product,
            message="No catalogue product matches that id or name.",
        )
    return ProductLookupResult(
        product_id=row["product_id"],
        found=True,
        status=LookupStatus.found,
        name=row["name"],
        description=row["description"],
        price=float(row["price"]),
        message=f"Found {row['name']}.",
    )


def lookup_stock(product_ref: str, size: str | None = None) -> StockResult:
    """Stock for one product. A requested size with no inventory row is not treated as zero."""
    requested = normalize_size(size)
    with connect() as connection:
        row, matches = _match_product(connection, product_ref)
        inventory = _inventory(connection, row["product_id"]) if row is not None else []
    if matches:
        choices = ", ".join(f"{item['name']} ({item['product_id']})" for item in matches)
        return StockResult(
            product_id=None,
            size=requested,
            found=False,
            status=LookupStatus.ambiguous,
            message=f"More than one product has that name: {choices}.",
        )
    if row is None:
        return StockResult(
            product_id=None,
            size=requested,
            found=False,
            status=LookupStatus.unknown_product,
            message="No catalogue product matches that id or name, so there is no stock to report.",
        )
    total = sum(item.quantity for item in inventory)
    if requested is None:
        return StockResult(
            product_id=row["product_id"],
            size=None,
            found=True,
            status=LookupStatus.found,
            inventory=inventory,
            quantity=None,
            total_stock=total,
            message=f"Recorded sizes for {row['name']}.",
        )
    match = next((item for item in inventory if item.size == requested), None)
    if match is None:
        recorded = ", ".join(item.size for item in inventory) or "none"
        return StockResult(
            product_id=row["product_id"],
            size=requested,
            found=True,
            status=LookupStatus.size_not_recorded,
            inventory=inventory,
            quantity=None,
            total_stock=total,
            message=(
                f"No inventory row for size {requested} on {row['name']}. "
                f"That is not zero stock. Recorded sizes: {recorded}."
            ),
        )
    if match.quantity == 0:
        return StockResult(
            product_id=row["product_id"],
            size=requested,
            found=True,
            status=LookupStatus.out_of_stock,
            inventory=inventory,
            quantity=0,
            total_stock=total,
            message=f"Size {requested} of {row['name']} is recorded and the quantity is 0.",
        )
    return StockResult(
        product_id=row["product_id"],
        size=requested,
        found=True,
        status=LookupStatus.found,
        inventory=inventory,
        quantity=match.quantity,
        total_stock=total,
        message=f"Size {requested} of {row['name']} has {match.quantity} in stock.",
    )


def _search_terms(query: str) -> list[str]:
    words = []
    for raw in query.lower().replace("-", " ").split():
        token = "".join(char for char in raw if char.isalnum())
        if len(token) < 3 or token in SEARCH_STOPWORDS:
            continue
        if token.endswith("s") and not token.endswith("ss") and len(token) > 4:
            token = token[:-1]
        if token not in words:
            words.append(token)
    return words


def _short_info(description: str) -> str:
    cleaned = " ".join(description.split())
    if len(cleaned) <= 140:
        return cleaned
    slice_ = cleaned[:140]
    cut = slice_.rfind(" ")
    shortened = slice_[: cut if cut > 40 else 140].rstrip()
    return f"{shortened}…"


def _string_list(raw: str) -> list[str]:
    parsed = json.loads(raw)
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        return []
    return parsed


def _product_from_row(row: sqlite3.Row, inventory: list[InventoryItem]) -> Product:
    filename = Path(row["image_file_path"]).name
    return Product(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        image_file_path=row["image_file_path"],
        image_url=f"/media/products/{filename}",
        colors=_string_list(row["colors"]),
        search_tags=_string_list(row["search_tags"]),
        price=float(row["price"]),
        inventory=inventory,
        total_stock=sum(item.quantity for item in inventory),
    )


def search_catalogue(query: str, size: str | None = None) -> tuple[SearchResult, list[Product]]:
    """Read-only search. A size keeps only rows with quantity greater than zero for that size."""
    requested = normalize_size(size)
    terms = _search_terms(query)
    if not terms:
        return (
            SearchResult(
                query=query.strip(),
                size=requested,
                match_count=0,
                returned_count=0,
                limit=SEARCH_LIMIT,
                message="Ask for a product category, such as hoodies.",
            ),
            [],
        )
    clauses = []
    params: list[str] = []
    for term in terms:
        like = f"%{term}%"
        clauses.append(
            """
            (
                lower(replace(name, '-', ' ')) LIKE ?
                OR lower(replace(garment_type, '-', ' ')) LIKE ?
                OR lower(replace(description, '-', ' ')) LIKE ?
                OR lower(replace(search_tags, '-', ' ')) LIKE ?
            )
            """
        )
        params.extend([like, like, like, like])
    sql = f"""
        SELECT product_id, name, garment_type, description, colors,
               search_tags, image_file_path, price
        FROM catalogue
        WHERE {" AND ".join(clauses)}
    """
    with connect() as connection:
        rows = connection.execute(sql, params).fetchall()
        ranked: list[tuple[int, str, sqlite3.Row, list[InventoryItem]]] = []
        for row in rows:
            name = row["name"].lower().replace("-", " ")
            garment = row["garment_type"].lower().replace("-", " ")
            tags = row["search_tags"].lower().replace("-", " ")
            description = row["description"].lower().replace("-", " ")
            score = 0
            for term in terms:
                if term in name:
                    score += 4
                if term in garment:
                    score += 3
                if term in tags:
                    score += 2
                if term in description:
                    score += 1
            inventory = _inventory(connection, row["product_id"])
            if requested is not None:
                on_hand = next((item.quantity for item in inventory if item.size == requested), None)
                if on_hand is None or on_hand <= 0:
                    continue
            ranked.append((score, row["name"].lower(), row, inventory))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    chosen = ranked[:SEARCH_LIMIT]
    products = [_product_from_row(row, inventory) for _score, _name, row, inventory in chosen]
    matches = []
    for product in products:
        size_quantity = None
        if requested is not None:
            size_quantity = next(item.quantity for item in product.inventory if item.size == requested)
        matches.append(
            SearchMatch(
                product_id=product.product_id,
                name=product.name,
                garment_type=product.garment_type,
                price=product.price,
                image_url=product.image_url,
                short_info=_short_info(product.description),
                size=requested,
                size_quantity=size_quantity,
            )
        )
    shown = len(matches)
    total = len(ranked)
    size_note = f" with size {requested} in stock" if requested else ""
    if total == 0:
        message = f"No catalogue products match that search{size_note}."
    elif total > shown:
        message = f"Found {total} catalogue products{size_note}. Showing the first {shown}."
    else:
        message = f"Found {total} catalogue products{size_note}."
    return (
        SearchResult(
            query=" ".join(terms),
            size=requested,
            match_count=total,
            returned_count=shown,
            limit=SEARCH_LIMIT,
            matches=matches,
            message=message,
        ),
        products,
    )


def suggest_alternatives(product_ref: str, size: str) -> tuple[AlternativeResult, list[Product]]:
    """Up to three other products of the same garment type with this size in stock."""
    requested = normalize_size(size)
    if requested is None:
        return (
            AlternativeResult(
                product_id=None,
                requested_size=None,
                available=False,
                message="Name a size, such as M, before asking for alternatives.",
            ),
            [],
        )
    with connect() as connection:
        row, matches = _match_product(connection, product_ref)
        if matches:
            choices = ", ".join(f"{item['name']} ({item['product_id']})" for item in matches)
            return (
                AlternativeResult(
                    product_id=None,
                    requested_size=requested,
                    available=False,
                    message=f"More than one product has that name: {choices}.",
                ),
                [],
            )
        if row is None:
            return (
                AlternativeResult(
                    product_id=None,
                    requested_size=requested,
                    available=False,
                    message="No catalogue product matches that id or name, so there are no alternatives.",
                ),
                [],
            )
        inventory = _inventory(connection, row["product_id"])
        garment = connection.execute(
            "SELECT garment_type FROM catalogue WHERE product_id = ?",
            (row["product_id"],),
        ).fetchone()["garment_type"]
        on_hand = next((item.quantity for item in inventory if item.size == requested), None)
        if on_hand is not None and on_hand > 0:
            return (
                AlternativeResult(
                    product_id=row["product_id"],
                    requested_size=requested,
                    garment_type=garment,
                    available=True,
                    message=(
                        f"Size {requested} of {row['name']} has {on_hand} in stock. "
                        "No alternatives are needed."
                    ),
                ),
                [],
            )
        others = connection.execute(
            """
            SELECT c.product_id, c.name, c.garment_type, c.description, c.colors,
                   c.search_tags, c.image_file_path, c.price, i.quantity
            FROM catalogue c
            JOIN inventory i ON i.product_id = c.product_id
            WHERE c.garment_type = ?
              AND c.product_id != ?
              AND i.size = ?
              AND i.quantity > 0
            ORDER BY i.quantity DESC, c.name COLLATE NOCASE
            LIMIT ?
            """,
            (garment, row["product_id"], requested, ALTERNATIVE_LIMIT),
        ).fetchall()
        products = []
        alternatives = []
        for other in others:
            other_inventory = _inventory(connection, other["product_id"])
            product = _product_from_row(other, other_inventory)
            products.append(product)
            alternatives.append(
                StockAlternative(
                    product_id=product.product_id,
                    name=product.name,
                    garment_type=product.garment_type,
                    price=product.price,
                    size=requested,
                    quantity=int(other["quantity"]),
                )
            )
        source_id = row["product_id"]
        source_name = row["name"]
    if not alternatives:
        reason = "not a recorded size" if on_hand is None else "quantity is 0"
        return (
            AlternativeResult(
                product_id=source_id,
                requested_size=requested,
                garment_type=garment,
                available=False,
                message=(
                    f"Size {requested} of {source_name} is unavailable ({reason}). "
                    f"No other {garment} has that size in stock."
                ),
            ),
            [],
        )
    return (
        AlternativeResult(
            product_id=row["product_id"],
            requested_size=requested,
            garment_type=garment,
            available=False,
            alternatives=alternatives,
            message=(
                f"Size {requested} of {source_name} is unavailable. "
                f"Showing {len(alternatives)} other {garment} with that size in stock."
            ),
        ),
        products,
    )
