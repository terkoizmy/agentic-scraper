import React, { useState } from 'react';
import { Search, Server, FileText, ExternalLink, Loader2 } from 'lucide-react';
import { apiClient } from '../../lib/api';

interface QueryResult {
  content: string;
  score: number;
  url: string;
  title?: string;
  language?: string;
}

interface QueryResponse {
  query: string;
  results: QueryResult[];
}

export const PlaygroundPage = () => {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(5);
  const [results, setResults] = useState<QueryResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError('');
    
    try {
      const res = await apiClient.post<QueryResponse>('/query', {
        q: query,
        top_k: topK
      });
      setResults(res.data.results || []);
      setHasSearched(true);
    } catch (err: any) {
      console.error('Failed to semantic search', err);
      setError(err?.response?.data?.detail || 'Gagal melakukan pencarian semantik.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto h-full flex flex-col">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-zinc-900 dark:text-white mb-2 flex items-center gap-3">
          <Server className="w-8 h-8 text-indigo-600" /> 
          RAG Playground
        </h1>
        <p className="text-zinc-500 text-lg">Uji coba kualitas Vector Database dan pencarian semantik ChromaDB Anda.</p>
      </div>

      <div className="bg-white dark:bg-zinc-900 rounded-2xl shadow-sm border border-zinc-200 dark:border-zinc-800 p-6 mb-8">
        <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-zinc-400" />
              <input 
                type="text" 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Deskripsikan apa yang ingin Anda cari dari Web Sources..."
                className="w-full pl-11 pr-4 py-3 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none transition-all shadow-sm"
              />
            </div>
          </div>
          <div className="w-full md:w-32">
            <input 
              type="number"
              min="1"
              max="20"
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              placeholder="Top K"
              className="w-full px-4 py-3 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none transition-all shadow-sm text-center"
              title="Jumlah maksimal hasil / Top K"
            />
          </div>
          <button 
            type="submit" 
            disabled={isLoading || !query.trim()}
            className="flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-xl font-medium shadow-md transition-all disabled:opacity-70 whitespace-nowrap"
          >
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
            <span>Cari Vektor</span>
          </button>
        </form>
        {error && <p className="mt-4 text-sm text-red-500 bg-red-50 p-2 rounded-lg border border-red-200">{error}</p>}
      </div>

      <div className="flex-1 overflow-auto">
        {!hasSearched && !isLoading && (
          <div className="h-40 flex flex-col items-center justify-center text-zinc-400 gap-3 border-2 border-dashed border-zinc-200 dark:border-zinc-800 rounded-2xl">
            <Server className="w-8 h-8 opacity-20" />
            <p>Masukkan kalimat luwes (query natural) untuk menguji hasil pencarian semantik.</p>
          </div>
        )}

        {isLoading && (
          <div className="h-40 flex flex-col items-center justify-center text-zinc-500 gap-4">
            <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
            <p>Sedang menghitung jarak vektor dokumen (Semantic Search)...</p>
          </div>
        )}

        {hasSearched && !isLoading && results.length === 0 && (
          <div className="h-40 flex items-center justify-center text-zinc-500 bg-zinc-50 dark:bg-zinc-900/50 rounded-2xl border border-zinc-200 dark:border-zinc-800">
            Tidak ada potongan dokumen (chunks) yang relevan berdasarkan kueri Anda.
          </div>
        )}

        {hasSearched && !isLoading && results.length > 0 && (
          <div className="space-y-6">
            <h3 className="font-semibold text-zinc-700 dark:text-zinc-300">
              Menampilkan {results.length} potongan dokumen paling identik:
            </h3>
            <div className="grid gap-4">
              {results.map((res, i) => (
                <div key={i} className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all hover:border-indigo-300 dark:hover:border-indigo-800/50">
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div className="flex-1">
                      <h4 className="font-bold text-zinc-900 dark:text-zinc-100 flex items-center gap-2">
                        <FileText className="w-4 h-4 text-indigo-500" />
                        {res.title || 'Tanpa Judul'}
                      </h4>
                      <a href={res.url} target="_blank" rel="noreferrer" className="text-sm text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300 hover:underline flex items-center gap-1 mt-1 w-fit">
                        <ExternalLink className="w-3 h-3" /> {res.url}
                      </a>
                    </div>
                    <div className="shrink-0 flex items-center gap-2 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 px-3 py-1.5 rounded-lg text-sm font-semibold border border-indigo-100 dark:border-indigo-800/40">
                      <span>Score:</span>
                      <span>{(res.score).toFixed(4)}</span>
                    </div>
                  </div>
                  <div className="relative mt-4">
                    <div className="text-sm text-zinc-700 dark:text-zinc-300 bg-zinc-50 dark:bg-zinc-950 p-4 rounded-xl font-mono whitespace-pre-wrap leading-relaxed max-h-64 overflow-y-auto overflow-x-hidden border border-zinc-100 dark:border-zinc-800/50">
                      {res.content}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PlaygroundPage;
