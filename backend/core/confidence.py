from typing import Any

from loguru import logger

from core.url_utils import _detect_code_query
from models.schemas import QueryResult

CONFIDENCE_THRESHOLD = 0.7
COSINE_WEIGHT = 0.4
LLM_WEIGHT = 0.6


async def _llm_evaluate_relevance(query: str, rag_results: list[QueryResult]) -> float:
    """Use LLM to score how relevant RAG results are to the query (0.0 - 1.0)."""
    if not rag_results:
        return 0.0

    results_text = "\n".join(
        [
            f"- [{r.title or r.url}]({r.url}): {r.content[:300]}..."
            for r in rag_results[:5]
        ]
    )

    prompt = f"""Anda adalah evaluator relevansi. Berikan skor 0.0-1.0 untuk hasil pencarian berikut terhadap query.
Query: {query}

Hasil pencarian:
{results_text}

Aturan:
- Skor 1.0 = Hasil sangat relevan dan cukup untuk menjawab query
- Skor 0.7-0.9 = Hasil cukup relevan, bisa menjawab dengan sedikit tambahan
- Skor 0.4-0.6 = Hasil sebagian relevan, perlu informasi tambahan
- Skor 0.0-0.3 = Hasil tidak relevan atau tidak cukup

Jawaban hanya berupa angka desimal tunggal (contoh: 0.75). Jangan berikan penjelasan lain."""

    try:
        from agent.brain import _call_minimax

        response = await _call_minimax([{"role": "user", "content": prompt}])
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "0.5")
        score = float(content.strip())
        return max(0.0, min(1.0, score))
    except (ValueError, KeyError, IndexError, Exception) as exc:
        logger.warning("LLM relevance evaluation failed: {}, defaulting to 0.5", exc)
        return 0.5


async def evaluate_rag_confidence(
    query: str, rag_results: list[QueryResult]
) -> tuple[float, bool]:
    """Evaluate RAG results confidence using hybrid approach.

    Args:
        query: The original user query
        rag_results: Results from RAG search

    Returns:
        Tuple of (confidence_score, should_deep_research)
        - confidence_score: 0.0 - 1.0
        - should_deep_research: True if confidence < 0.7 AND query is code-related
    """
    if not rag_results:
        logger.debug("No RAG results, confidence = 0.0")
        return 0.0, _detect_code_query(query)

    cosine_scores = [r.score for r in rag_results]
    avg_cosine = sum(cosine_scores) / len(cosine_scores)

    is_code = _detect_code_query(query)

    if not is_code:
        logger.debug("Non-code query, using cosine only: {:.2f}", avg_cosine)
        confidence = avg_cosine
    else:
        llm_score = await _llm_evaluate_relevance(query, rag_results)
        confidence = (avg_cosine * COSINE_WEIGHT) + (llm_score * LLM_WEIGHT)
        logger.info(
            "Code query confidence: cosine={:.2f}, llm={:.2f}, hybrid={:.2f}",
            avg_cosine,
            llm_score,
            confidence,
        )

    should_deep_research = is_code and confidence < CONFIDENCE_THRESHOLD

    logger.debug(
        "Confidence evaluation: query='{}', is_code={}, confidence={:.2f}, should_deep_research={}",
        query[:50],
        is_code,
        confidence,
        should_deep_research,
    )

    return round(confidence, 4), should_deep_research
