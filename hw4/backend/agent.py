"""Ask Dan: PydanticAI agent wiring for Campus Customs."""

from __future__ import annotations

import asyncio
import os
import uuid
from dataclasses import dataclass, field
from pathlib import Path

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart, UserPromptPart
from pydantic_ai.exceptions import UsageLimitExceeded
from pydantic_ai.usage import UsageLimits

from audit import record_event
from models import (
    AlternativeResult,
    ChatReply,
    ChatResponse,
    Customer,
    PageContext,
    Product,
    ProductLookupResult,
    SearchResult,
    ShoppingContext,
    StockResult,
)
from tools import lookup_product as fetch_product
from tools import lookup_stock as fetch_stock
from tools import search_catalogue as fetch_search
from tools import shopping_context
from tools import suggest_alternatives as fetch_alternatives

BACKEND_DIR = Path(__file__).resolve().parent
PROMPT_PATH = BACKEND_DIR / "prompts" / "prompt.md"
PORTKEY_BASE_URL = "https://api.portkey.ai/v1"
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5.6-luna").strip() or "gpt-5.6-luna"
REQUEST_LIMIT = 6
TOOL_CALLS_LIMIT = 8
AGENT_TIMEOUT_SECONDS = 60.0

_agent: Agent[AgentDeps, ChatReply] | None = None


@dataclass
class AgentDeps:
    customer: Customer | None
    page_context: PageContext
    run_id: str
    products: list[Product] = field(default_factory=list)


def portkey_client() -> AsyncOpenAI:
    """Portkey client from ~/.env. The key is not stored in this project."""
    load_dotenv(Path.home() / ".env")
    key = (os.getenv("PORTKEY_API_KEY") or "").strip()
    if not key:
        raise RuntimeError("PORTKEY_API_KEY is missing from ~/.env")
    return AsyncOpenAI(
        api_key=key,
        base_url=PORTKEY_BASE_URL,
        default_headers={"x-portkey-api-key": key},
        timeout=AGENT_TIMEOUT_SECONDS,
        max_retries=0,
    )


def build_agent() -> Agent[AgentDeps, ChatReply]:
    instructions = PROMPT_PATH.read_text(encoding="utf-8").strip()
    model = OpenAIResponsesModel(MODEL_NAME, provider=OpenAIProvider(openai_client=portkey_client()))
    agent = Agent(
        model,
        deps_type=AgentDeps,
        output_type=ChatReply,
        instructions=instructions,
        retries=0,
    )

    @agent.tool
    async def shopping_context_tool(ctx: RunContext[AgentDeps]) -> ShoppingContext:
        """Return the session shopper's name and email, the open page, and the catalogue product on that page."""
        args = f"page={ctx.deps.page_context.page} product_id={ctx.deps.page_context.product_id or ''}"
        try:
            result = shopping_context(ctx.deps.customer, ctx.deps.page_context)
        except Exception as exc:
            _log_tool(ctx.deps.run_id, "shopping_context", args, exc)
            raise
        _log_tool(
            ctx.deps.run_id,
            "shopping_context",
            args,
            f"signed_in={result.signed_in} product_found={result.product_found} product_id={result.product_id or ''}",
        )
        return result

    @agent.tool
    async def lookup_product(ctx: RunContext[AgentDeps], product_ref: str) -> ProductLookupResult:
        """Look up one product's name, description, and price by catalogue product_id or exact name."""
        args = f"product_ref={product_ref}"
        try:
            result = fetch_product(product_ref)
        except Exception as exc:
            _log_tool(ctx.deps.run_id, "lookup_product", args, exc)
            raise
        _log_tool(
            ctx.deps.run_id,
            "lookup_product",
            args,
            f"status={result.status} product_id={result.product_id or ''} price={result.price}",
        )
        return result

    @agent.tool
    async def lookup_stock(ctx: RunContext[AgentDeps], product_ref: str, size: str | None = None) -> StockResult:
        """Look up recorded stock for a product. Pass a size such as M when the shopper asks about one size."""
        args = f"product_ref={product_ref} size={size or ''}"
        try:
            result = fetch_stock(product_ref, size)
        except Exception as exc:
            _log_tool(ctx.deps.run_id, "lookup_stock", args, exc)
            raise
        _log_tool(
            ctx.deps.run_id,
            "lookup_stock",
            args,
            f"status={result.status} product_id={result.product_id or ''} size={result.size or ''} quantity={result.quantity}",
        )
        return result

    @agent.tool
    async def search_catalogue(ctx: RunContext[AgentDeps], query: str, size: str | None = None) -> SearchResult:
        """Search the catalogue. Pass a size such as M to keep only products with that size in stock."""
        args = f"query={query} size={size or ''}"
        try:
            result, products = fetch_search(query, size)
        except Exception as exc:
            _log_tool(ctx.deps.run_id, "search_catalogue", args, exc)
            raise
        ctx.deps.products = products
        _log_tool(
            ctx.deps.run_id,
            "search_catalogue",
            args,
            f"match_count={result.match_count} returned_count={result.returned_count}",
        )
        return result

    @agent.tool
    async def suggest_alternatives(ctx: RunContext[AgentDeps], product_ref: str, size: str) -> AlternativeResult:
        """When a requested size is unavailable, return up to three similar in-stock products."""
        args = f"product_ref={product_ref} size={size}"
        try:
            result, products = fetch_alternatives(product_ref, size)
        except Exception as exc:
            _log_tool(ctx.deps.run_id, "suggest_alternatives", args, exc)
            raise
        ctx.deps.products = products
        _log_tool(
            ctx.deps.run_id,
            "suggest_alternatives",
            args,
            f"available={result.available} alternatives={len(result.alternatives)}",
        )
        return result

    return agent


def _log_tool(run_id: str, tool_name: str, args_summary: str, outcome: object) -> None:
    failed = isinstance(outcome, Exception)
    record_event(
        run_id,
        "tool_failure" if failed else "tool_result",
        tool_name,
        args_summary,
        type(outcome).__name__ if failed else str(outcome),
        None,
    )


def configured_limits() -> UsageLimits:
    return UsageLimits(request_limit=REQUEST_LIMIT, tool_calls_limit=TOOL_CALLS_LIMIT)


def get_agent() -> Agent[AgentDeps, ChatReply]:
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


async def run_chat(
    message: str,
    page_context: PageContext,
    customer: Customer | None,
    message_history: list[ModelMessage] | None = None,
) -> ChatResponse:
    run_id = uuid.uuid4().hex
    deps = AgentDeps(customer=customer, page_context=page_context, run_id=run_id)
    stop_reason = "completed"
    try:
        result = await asyncio.wait_for(
            get_agent().run(
                message,
                deps=deps,
                message_history=message_history or None,
                usage_limits=configured_limits(),
            ),
            timeout=AGENT_TIMEOUT_SECONDS,
        )
    except UsageLimitExceeded:
        stop_reason = "limits"
        raise
    except TimeoutError:
        stop_reason = "timeout"
        raise
    except Exception:
        stop_reason = "error"
        raise
    finally:
        record_event(
            run_id,
            "run_finished",
            None,
            "",
            f"products={len(deps.products)}",
            stop_reason,
        )
    reply = result.output.reply.strip()
    if not reply:
        reply = "I didn’t catch that. Ask me again in a sentence or two."
    return ChatResponse(reply=reply, products=list(deps.products))


def prior_messages(turns: list[tuple[str, str]]) -> list[ModelMessage]:
    """Recent user and assistant text for the next run. Tool traces are not replayed."""
    messages: list[ModelMessage] = []
    for role, content in turns:
        if role == "user":
            messages.append(ModelRequest(parts=[UserPromptPart(content=content)]))
        elif role == "assistant":
            messages.append(ModelResponse(parts=[TextPart(content=content)]))
    return messages
