"""Structured types for the Campus Customs API and Ask Dan."""

from enum import Enum

from pydantic import BaseModel, Field


class Customer(BaseModel):
    user_id: int
    name: str
    email: str
    first_name: str | None
    last_name: str | None


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    password_confirmation: str


class LoginRequest(BaseModel):
    email: str
    password: str


class InventoryItem(BaseModel):
    size: str
    quantity: int


class Product(BaseModel):
    product_id: str
    name: str
    garment_type: str
    description: str
    image_file_path: str
    image_url: str
    colors: list[str]
    search_tags: list[str]
    price: float
    inventory: list[InventoryItem]
    total_stock: int


class PageContext(BaseModel):
    page: str
    product_id: str | None = None


class ChatRequest(BaseModel):
    message: str
    page_context: PageContext


class ShoppingContext(BaseModel):
    """Signed-in identity and the open page. Product fields are resolved from the catalogue."""

    signed_in: bool
    name: str | None
    email: str | None
    page: str
    product_id: str | None
    product_name: str | None = None
    colors: list[str] = Field(default_factory=list)
    product_found: bool = False
    message: str


class LookupStatus(str, Enum):
    found = "found"
    unknown_product = "unknown_product"
    ambiguous = "ambiguous"
    size_not_recorded = "size_not_recorded"
    out_of_stock = "out_of_stock"


class ProductLookupResult(BaseModel):
    """Description and price for one catalogue product."""

    product_id: str | None
    found: bool
    status: LookupStatus
    name: str | None = None
    description: str | None = None
    price: float | None = None
    message: str


class StockResult(BaseModel):
    """Stock for one product, optionally one size. Zero is recorded stock; a missing size is not zero."""

    product_id: str | None
    size: str | None
    found: bool
    status: LookupStatus
    inventory: list[InventoryItem] = Field(default_factory=list)
    quantity: int | None = None
    total_stock: int = 0
    message: str


class SearchMatch(BaseModel):
    """One catalogue hit. Prices and ids come from the row, not from the model."""

    product_id: str
    name: str
    garment_type: str
    price: float
    image_url: str
    short_info: str
    size: str | None = None
    size_quantity: int | None = None


class SearchResult(BaseModel):
    """Bounded catalogue search. returned_count never exceeds the cap."""

    query: str
    size: str | None = None
    match_count: int
    returned_count: int
    limit: int
    matches: list[SearchMatch] = Field(default_factory=list)
    message: str


class StockAlternative(BaseModel):
    """Another product of the same garment type with the requested size in stock."""

    product_id: str
    name: str
    garment_type: str
    price: float
    size: str
    quantity: int


class AlternativeResult(BaseModel):
    """Up to three substitutes. Empty when the size is already in stock or none exist."""

    product_id: str | None
    requested_size: str | None
    garment_type: str | None = None
    available: bool
    alternatives: list[StockAlternative] = Field(default_factory=list)
    message: str


class ChatReply(BaseModel):
    """Model text only. Product cards are attached from the search tool."""

    reply: str


class ChatResponse(BaseModel):
    reply: str
    products: list[Product]


class ChatHistoryMessage(BaseModel):
    id: int
    role: str
    content: str
    products: list[Product] = Field(default_factory=list)
    created_at: str
