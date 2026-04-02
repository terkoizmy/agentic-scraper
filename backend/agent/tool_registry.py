import asyncio
import json
from typing import Any, Callable, Optional

from fastapi import HTTPException
from loguru import logger

from api.query import rag_query
from api.scrape import crawl_docs, fetch_page, store_content
from core.confidence import evaluate_rag_confidence
from core.url_utils import COMPLEXITY_WEBSITE_COUNT, _detect_code_query, _detect_query_complexity, _is_docs_url, _is_relevant_url
from models.schemas import CrawlRequest, DeepResearchResponse, FetchRequest, FetchResponse, QueryRequest, QueryResult, StoreRequest


def _get_error_msg(exc: Exception) -> str:
    """Extract readable error message from exceptions."""
    if isinstance(exc, HTTPException):
        return f"{exc.status_code}: {exc.detail}"
    return str(exc)


async def execute_scrape_page(args: dict[str, Any], session_id: Optional[str] = None) -> dict[str, Any]:
    """Execute scrape_page tool."""
    from agent.memory import has_rag_query_in_session

    if session_id and not has_rag_query_in_session(session_id):
        from core.url_utils import _extract_topic_from_url
        query = _extract_topic_from_url(args.get("url", ""))
        logger.info("scrape_page called without prior rag_query, auto-searching for '{}'", query)

        search_result = await execute_web_search({"query": query, "max_results": 5})
        return {
            "status": "requires_web_search_first",
            "message": f"Web search executed for '{query}'. Review results before scraping:",
            "search_results": search_result.get("results", []),
            "suggestion": "After reviewing search results, call scrape_page again or use rag_query to store relevant content.",
        }

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


async def execute_web_search(args: dict[str, Any]) -> dict[str, Any]:
    """Execute web_search tool using DuckDuckGo."""
    try:
        from ddgs import DDGS
        query = args.get("query")
        if not query:
            return {"error": "Query is required"}
        max_results = args.get("max_results", 5)
        
        def _search():
            return list(DDGS().text(query, max_results=max_results))
            
        results = await asyncio.to_thread(_search)
        return {"query": query, "results": results}
    except ImportError:
        return {"error": "Package 'ddgs' is not installed."}
    except Exception as exc:
        logger.error("Web search failed: {}", exc)
        return {"error": _get_error_msg(exc)}


async def execute_deep_research(args: dict[str, Any]) -> dict[str, Any]:
    """Execute deep_research tool for code-related queries with low confidence."""
    query = args.get("query", "")
    if not query:
        return {"error": "Query is required for deep research"}

    deep_crawl = args.get("deep_crawl", False)

    complexity = args.get("complexity")
    if not complexity:
        complexity = _detect_query_complexity(query)

    website_count = COMPLEXITY_WEBSITE_COUNT.get(complexity, 5)
    logger.info("Deep research: query='{}', complexity='{}', websites={}", query[:50], complexity, website_count)

    try:
        rag_req = QueryRequest(q=query, top_k=5)
        rag_res = await rag_query(rag_req)
        rag_results = rag_res.results
    except Exception as exc:
        logger.warning("Deep research: RAG query failed, proceeding with empty results: {}", exc)
        rag_results = []

    confidence, should_deep_research = await evaluate_rag_confidence(query, rag_results)

    if not should_deep_research:
        logger.info("Deep research: confidence {:.2f} >= 0.7, skipping web search", confidence)
        return {
            "status": "sufficient",
            "confidence": confidence,
            "rag_results": [r.model_dump() for r in rag_results],
            "websites_searched": 0,
            "websites_scraped": 0,
            "total_chunks_stored": 0,
            "deep_crawl_results": {},
        }

    logger.info("Deep research: confidence {:.2f} < 0.7, proceeding with web search", confidence)

    try:
        from ddgs import DDGS

        def _search():
            return list(DDGS().text(query, max_results=website_count))

        search_results = await asyncio.to_thread(_search)
    except ImportError:
        return {"error": "Package 'ddgs' is not installed."}
    except Exception as exc:
        logger.error("Deep research: web search failed: {}", exc)
        return {"error": f"Web search failed: {_get_error_msg(exc)}"}

    urls = [r.get("href", "") for r in search_results if _is_relevant_url(r.get("href", ""))]
    logger.info("Deep research: found {} relevant URLs from {} search results", len(urls), len(search_results))

    if not urls:
        return {
            "status": "no_relevant_urls",
            "confidence": confidence,
            "rag_results": [r.model_dump() for r in rag_results],
            "websites_searched": 0,
            "websites_scraped": 0,
            "total_chunks_stored": 0,
            "deep_crawl_results": {},
        }

    scrape_tasks = [fetch_page(FetchRequest(url=url)) for url in urls]
    scraped_results = await asyncio.gather(*scrape_tasks, return_exceptions=True)

    valid_scrape_results: list[FetchResponse] = []
    for s in scraped_results:
        if isinstance(s, FetchResponse):
            valid_scrape_results.append(s)
        elif isinstance(s, Exception):
            logger.warning("Scrape failed: {}", s)

    total_chunks = 0
    for scrape_result in valid_scrape_results:
        try:
            chunks, _ = await _store_scrape_result(scrape_result)
            total_chunks += chunks
        except Exception as exc:
            logger.warning("Failed to store scrape result for {}: {}", scrape_result.url, exc)

    deep_crawl_results = {}
    if deep_crawl:
        doc_urls = [s.url for s in valid_scrape_results if _is_docs_url(s.url)]
        logger.info("Deep research: starting deep crawl for {} doc URLs", len(doc_urls))
        for doc_url in doc_urls:
            try:
                crawl_req = CrawlRequest(base_url=doc_url, depth=2, max_pages=30)
                crawl_result = await crawl_docs(crawl_req)
                deep_crawl_results[doc_url] = crawl_result.model_dump()
            except Exception as exc:
                logger.warning("Deep crawl failed for {}: {}", doc_url, exc)

    return {
        "status": "deep_research_completed",
        "confidence": confidence,
        "rag_results": [r.model_dump() for r in rag_results],
        "websites_searched": len(urls),
        "websites_scraped": len(valid_scrape_results),
        "total_chunks_stored": total_chunks,
        "deep_crawl_results": deep_crawl_results,
    }


async def _store_scrape_result(scrape_result) -> tuple[int, bool]:
    """Store a FetchResponse to the pipeline."""
    from api.scrape import _run_pipeline

    try:
        chunks, is_dupe = await _run_pipeline(
            url=scrape_result.url,
            markdown=scrape_result.markdown,
            title=scrape_result.title,
            language=scrape_result.language,
        )
        return chunks, is_dupe
    except Exception as exc:
        logger.error("Failed to store scrape result for {}: {}", scrape_result.url, exc)
        return 0, False


TOOL_DISPATCHER: dict[str, Callable] = {
    "scrape_page": execute_scrape_page,
    "crawl_docs": execute_crawl_docs,
    "rag_query": execute_rag_query,
    "store_content": execute_store_content,
    "web_search": execute_web_search,
    "deep_research": execute_deep_research,
}


async def dispatch_tool_call(tool_name: str, args_str: str, session_id: Optional[str] = None) -> dict[str, Any]:
    """Parse JSON arguments and invoke the corresponding tool module."""
    logger.info("Agent parsing tool call: {} {} (session_id={})", tool_name, args_str, session_id)
    
    try:
        args = json.loads(args_str)
    except json.JSONDecodeError:
        logger.error("Invalid JSON arguments for tool: {}", tool_name)
        return {"error": "Invalid JSON arguments"}

    handler = TOOL_DISPATCHER.get(tool_name)
    if not handler:
        logger.error("Tool '{}' not defined in registry", tool_name)
        return {"error": f"Tool '{tool_name}' not found"}

    if tool_name in ("scrape_page",):
        return await handler(args, session_id)
    return await handler(args)
