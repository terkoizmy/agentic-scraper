TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "scrape_page",
            "description": "Scrape satu halaman URL dan kembalikan konten bersih dalam format Markdown",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL halaman yang ingin di-scrape"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crawl_docs",
            "description": "Crawl semua halaman dari sebuah dokumentasi atau website, lalu simpan ke database",
            "parameters": {
                "type": "object",
                "properties": {
                    "base_url": {"type": "string", "description": "URL awal/base dokumentasi"},
                    "depth":    {"type": "integer", "description": "Kedalaman crawling (default: 2)"},
                    "max_pages":{"type": "integer", "description": "Maksimum halaman yang di-crawl (default: 50)"}
                },
                "required": ["base_url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rag_query",
            "description": "Cari konten yang relevan di database menggunakan semantic search",
            "parameters": {
                "type": "object",
                "properties": {
                    "query":  {"type": "string",  "description": "Query pencarian natural language"},
                    "top_k":  {"type": "integer", "description": "Jumlah hasil yang dikembalikan (default: 5)"},
                    "language": {"type": "string","description": "Filter bahasa: 'id' atau 'en' (opsional)"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "store_content",
            "description": "Simpan konten Markdown ke database (embed + store ke vector DB)",
            "parameters": {
                "type": "object",
                "properties": {
                    "url":      {"type": "string", "description": "URL sumber konten"},
                    "markdown": {"type": "string", "description": "Konten Markdown yang akan disimpan"}
                },
                "required": ["url", "markdown"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Cari informasi di internet menggunakan mesin pencari (DuckDuckGo). Gunakan ini jika Anda butuh mencari URL dokumentasi yang benar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query":  {"type": "string", "description": "Kata kunci pencarian natural language"},
                    "max_results": {"type": "integer", "description": "Jumlah hasil yang dikembalikan (default: 5)"}
                },
                "required": ["query"]
            }
        }
    }
]
