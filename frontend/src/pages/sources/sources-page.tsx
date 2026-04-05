import { useEffect, useState } from 'react';
import axios from 'axios';
import { Database, Plus, CheckCircle2, XCircle, Zap, Trash2, Power, Loader2 } from 'lucide-react';
import type { SourceDto } from '../../types/dtos';
import { apiClient } from '../../lib/api';
import { AddSourceModal } from './components/add-source-modal';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const SourcesPage = () => {
  const [sources, setSources] = useState<SourceDto[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [scrapingId, setScrapingId] = useState<string | null>(null);

  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    try {
      setIsLoading(true);
      const res = await axios.get<SourceDto[]>(`${API_BASE_URL}/sources`);
      setSources(res.data);
    } catch (error) {
      console.error('Failed to fetch sources', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleScrapeNow = async (source: SourceDto) => {
    try {
      setScrapingId(source.id);
      if (source.source_type === 'docs') {
        await apiClient.post('/scrape/crawl', { base_url: source.url, depth: 2, max_pages: 50 });
      } else {
        await apiClient.post('/scrape/fetch', { url: source.url });
      }
      fetchSources();
    } catch (error) {
      console.error('Failed to trigger scrape', error);
      alert('Gagal memulai proses scrape');
    } finally {
      setScrapingId(null);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Yakin ingin menghapus source ini beserta seluruh histori datanya?')) return;
    try {
      await apiClient.delete(`/sources/${id}`);
      fetchSources();
    } catch (error) {
      console.error('Failed to delete source', error);
      alert('Gagal menghapus source');
    }
  };

  const handleToggleActive = async (id: string, currentStatus: boolean) => {
    try {
      await apiClient.patch(`/sources/${id}`, { is_active: !currentStatus });
      fetchSources();
    } catch (error) {
      console.error('Failed to toggle status', error);
      alert('Gagal mengubah status');
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto h-full flex flex-col">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-zinc-900 dark:text-white mb-2 flex items-center gap-3">
            <Database className="w-8 h-8 text-blue-600" /> 
            Web Sources
          </h1>
          <p className="text-zinc-500 text-lg">Daftar domain dan situs yang dipantau oleh sistem.</p>
        </div>
        <button 
          onClick={() => setIsAddModalOpen(true)}
          className="flex items-center gap-2 bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-zinc-200 text-white dark:text-zinc-900 px-5 py-2.5 rounded-xl font-medium shadow-md transition-all"
        >
          <Plus className="w-5 h-5" />
          <span>Tambah Source</span>
        </button>
      </div>

      <div className="flex-1 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-sm overflow-hidden flex flex-col">
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-zinc-500 uppercase bg-zinc-50 dark:bg-zinc-950/80 border-b border-zinc-200 dark:border-zinc-800 sticky top-0">
              <tr>
                <th className="px-6 py-4 font-semibold">Nama Situs</th>
                <th className="px-6 py-4 font-semibold">URL Dasar</th>
                <th className="px-6 py-4 font-semibold">Tipe</th>
                <th className="px-6 py-4 font-semibold">Status</th>
                <th className="px-6 py-4 font-semibold">Terakhir Scrape</th>
                <th className="px-6 py-4 font-semibold text-right">Aksi</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-zinc-400">
                    Memuat data sources...
                  </td>
                </tr>
              ) : sources.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-zinc-400">
                    <div className="flex flex-col items-center gap-3">
                      <Database className="w-12 h-12 opacity-20" />
                      <p>Belum ada web source yang terdaftar.</p>
                    </div>
                  </td>
                </tr>
              ) : (
                sources.map((src) => (
                  <tr key={src.id} className="border-b border-zinc-100 dark:border-zinc-800/50 hover:bg-zinc-50 dark:hover:bg-zinc-800/30 transition-colors">
                    <td className="px-6 py-4 font-semibold truncate max-w-[200px]">{src.name}</td>
                    <td className="px-6 py-4 text-blue-600 dark:text-blue-400 truncate max-w-[300px]">
                      <a href={src.url} target="_blank" rel="noreferrer" className="hover:underline">
                        {src.url}
                      </a>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-1 bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 rounded-md text-xs font-semibold uppercase tracking-wider">
                        {src.source_type}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {src.is_active ? 
                        <div className="flex items-center gap-2 text-green-600 dark:text-green-500 font-medium">
                          <CheckCircle2 className="w-4 h-4" /> Aktif
                        </div> : 
                        <div className="flex items-center gap-2 text-zinc-400 font-medium">
                          <XCircle className="w-4 h-4" /> Nonaktif
                        </div>
                      }
                    </td>
                    <td className="px-6 py-4 text-zinc-500">
                      {src.last_scraped_at ? new Date(src.last_scraped_at).toLocaleString('id-ID') : 'Belum Pernah'}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button 
                          onClick={() => handleScrapeNow(src)}
                          disabled={scrapingId === src.id}
                          title="Scrape Sekarang"
                          className="p-2 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/50 rounded-lg transition-colors disabled:opacity-50"
                        >
                          {scrapingId === src.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                        </button>
                        <button 
                          onClick={() => handleToggleActive(src.id, src.is_active)}
                          title={src.is_active ? "Nonaktifkan" : "Aktifkan"}
                          className={`p-2 rounded-lg transition-colors ${
                            src.is_active ? "bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 hover:bg-amber-100 dark:hover:bg-amber-900/50" :
                            "bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400 hover:bg-green-100 dark:hover:bg-green-900/50"
                          }`}
                        >
                          <Power className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => handleDelete(src.id)}
                          title="Hapus Source"
                          className="p-2 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/50 rounded-lg transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <AddSourceModal 
        isOpen={isAddModalOpen} 
        onClose={() => setIsAddModalOpen(false)} 
        onSuccess={fetchSources} 
      />
    </div>
  );
};

export default SourcesPage;
