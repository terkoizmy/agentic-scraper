import re
from typing import Literal

CODE_URL_PATTERNS = [
    r"github\.com",
    r"gitlab\.com",
    r"docs\.",
    r"api\.",
    r"developer\.",
    r"dev\.",
    r"stackoverflow\.com",
    r"pypi\.org",
    r"npmjs\.com",
    r"crates\.io",
    r"readthedocs\.",
    r"readthedocs\.io",
    r"\.io/docs",
    r"/v\d+/",
    r"/api/",
    r"dev\.to",
    r"medium\.com/@",
    r"geeksforgeeks\.org",
    r"tutorialspoint\.com",
]

CODE_KEYWORDS = [
    "function",
    "class",
    "method",
    "api",
    "code",
    "python",
    "javascript",
    "typescript",
    "react",
    "fastapi",
    "flask",
    "django",
    "sql",
    "database",
    "endpoint",
    "module",
    "import",
    "export",
    "package",
    "library",
    "async",
    "await",
    "callback",
    "promise",
    "runtime",
    "compiler",
    "framework",
    "repository",
    "commit",
    "branch",
    "deployment",
    "docker",
    "kubernetes",
    "ci/cd",
    "configuration",
    "install",
    "setup",
    "requirement",
    "dependency",
    "version",
    "error",
    "exception",
    "debug",
]

COMPLEXITY_KEYWORDS = {
    "high": [
        "tutorial",
        "guide",
        "advanced",
        "architecture",
        "design pattern",
        "optimization",
        "performance",
        "best practice",
        "complete",
        "full stack",
        "enterprise",
        "production",
    ],
    "medium": [
        "example",
        "how to",
        "usage",
        "implementation",
        "sample",
        "demo",
        "use case",
        "integration",
        "setup",
        "config",
    ],
}


def _is_relevant_url(url: str) -> bool:
    """Check if URL is relevant for code-related queries."""
    if not url:
        return False
    url_lower = url.lower()
    return any(re.search(p, url_lower) for p in CODE_URL_PATTERNS)


def _is_docs_url(url: str) -> bool:
    """Check if URL is a documentation site."""
    if not url:
        return False
    url_lower = url.lower()
    docs_patterns = [
        r"docs\.",
        r"developer\.",
        r"dev\.",
        r"readthedocs",
        r"/docs/",
        r"/documentation/",
        r"\.io/docs",
    ]
    return any(re.search(p, url_lower) for p in docs_patterns)


def _detect_code_query(query: str) -> bool:
    """Detect if query is code-related based on keywords."""
    if not query:
        return False
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in CODE_KEYWORDS)


def _detect_query_complexity(query: str) -> Literal["low", "medium", "high"]:
    """Detect query complexity based on keyword matching.

    Returns:
        - 'low': Basic questions (what is, define, simple)
        - 'medium': Moderate complexity (examples, usage, how to)
        - 'high': Complex topics (tutorials, architecture, advanced)
    """
    if not query:
        return "medium"

    query_lower = query.lower()

    high_count = sum(1 for kw in COMPLEXITY_KEYWORDS["high"] if kw in query_lower)
    medium_count = sum(1 for kw in COMPLEXITY_KEYWORDS["medium"] if kw in query_lower)

    if high_count >= 2:
        return "high"
    elif high_count == 1 and medium_count >= 2:
        return "high"
    elif medium_count >= 3:
        return "medium"
    elif medium_count >= 1:
        return "medium"
    else:
        return "low"


COMPLEXITY_WEBSITE_COUNT = {
    "low": 3,
    "medium": 5,
    "high": 8,
}
