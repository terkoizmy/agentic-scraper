import json
from typing import Any, Callable

from fastapi import HTTPException
from loguru import logger

from api.query import rag_query
from api.scrape import crawl_docs, fetch_page, store_content
from models.schemas import CrawlRequest, FetchRequest, QueryRequest, StoreRequest


def _get_error_msg(exc: Exception) -> str:
    """Extract readable error message from exceptions."""
    if isinstance(exc, HTTPException):
        return f"{exc.status_code}: {exc.detail}"
    return str(exc)


async def execute_scrape_page(args: dict[str, Any]) -> dict[str, Any]:
    """Execute scrape_page tool."""
    try:
        req = FetchRequest(**args)
        res = await fetch_page(req)
        return res.model_dump()
    except Exception as exc:
        return {"error": _get_error_msg(exc)}


async def execute_crawl_docs(args: dict[str, Any]) -> dict[str, Any]:
    """Execute crawl_docs tool."""
    try:
        req = CrawlRequest(**args)
        res = await crawl_docs(req)
        return res.model_dump()
    except Exception as exc:
        return {"error": _get_error_msg(exc)}


async def execute_rag_query(args: dict[str, Any]) -> dict[str, Any]:
    """Execute rag_query tool."""
    try:
        query_payload = {
            "q": args.get("query", ""),
            "top_k": args.get("top_k", 5),
        }
        if "language" in args:
            query_payload["language"] = args["language"]
            
        req = QueryRequest(**query_payload)
        res = await rag_query(req)
        return res.model_dump()
    except Exception as exc:
        return {"error": _get_error_msg(exc)}


async def execute_store_content(args: dict[str, Any]) -> dict[str, Any]:
    """Execute store_content tool."""
    try:
        req = StoreRequest(**args)
        res = await store_content(req)
        return res.model_dump()
    except Exception as exc:
        return {"error": _get_error_msg(exc)}


TOOL_DISPATCHER: dict[str, Callable] = {
    "scrape_page": execute_scrape_page,
    "crawl_docs": execute_crawl_docs,
    "rag_query": execute_rag_query,
    "store_content": execute_store_content,
}


async def dispatch_tool_call(tool_name: str, args_str: str) -> dict[str, Any]:
    """Parse JSON arguments and invoke the corresponding tool module."""
    logger.info("Agent parsing tool call: {} {}", tool_name, args_str)
    
    try:
        args = json.loads(args_str)
    except json.JSONDecodeError:
        logger.error("Invalid JSON arguments for tool: {}", tool_name)
        return {"error": "Invalid JSON arguments"}

    handler = TOOL_DISPATCHER.get(tool_name)
    if not handler:
        logger.error("Tool '{}' not defined in registry", tool_name)
        return {"error": f"Tool '{tool_name}' not found"}

    return await handler(args)
