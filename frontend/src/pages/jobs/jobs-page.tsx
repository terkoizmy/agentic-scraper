import { useEffect, useState } from 'react';
import axios from 'axios';
import { Activity, Clock, Zap, AlertTriangle, FileText, CheckCircle2 } from 'lucide-react';
import type { JobDto } from '../../types/dtos';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const JobsPage = () => {
  const [jobs, setJobs] = useState<JobDto[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      setIsLoading(true);
      const res = await axios.get<JobDto[]>(`${API_BASE_URL}/scrape/jobs`);
      setJobs(res.data);
    } catch (error) {
      console.error('Failed to fetch jobs', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto h-full flex flex-col">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-zinc-900 dark:text-white mb-2 flex items-center gap-3">
            <Activity className="w-8 h-8 text-amber-500" />
            Riwayat Scraping Jobs
          </h1>
          <p className="text-zinc-500 text-lg">Catatan audit lengkap aktivitas background scraping.</p>
        </div>
      </div>

      <div className="flex-1 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-sm overflow-hidden flex flex-col">
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-zinc-500 uppercase bg-zinc-50 dark:bg-zinc-950/80 border-b border-zinc-200 dark:border-zinc-800 sticky top-0">
              <tr>
                <th className="px-6 py-4 font-semibold">Tipe / Trigger</th>
                <th className="px-6 py-4 font-semibold">Status</th>
                <th className="px-6 py-4 font-semibold">Chunks</th>
                <th className="px-6 py-4 font-semibold">Error Detail</th>
                <th className="px-6 py-4 font-semibold">Waktu Mulai</th>
                <th className="px-6 py-4 font-semibold">Waktu Selesai</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-zinc-400">
                    Memuat riwayat jobs...
                  </td>
                </tr>
              ) : jobs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-zinc-400">
                    <div className="flex flex-col items-center gap-3">
                      <Clock className="w-12 h-12 opacity-20" />
                      <p>Belum ada riwayat job scraping sama sekali.</p>
                    </div>
                  </td>
                </tr>
              ) : (
                jobs.map((job) => (
                  <tr key={job.id} className="border-b border-zinc-100 dark:border-zinc-800/50 hover:bg-zinc-50 dark:hover:bg-zinc-800/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        {job.trigger === 'manual' ? <Zap className="w-4 h-4 text-blue-500" /> : <Clock className="w-4 h-4 text-zinc-500" />}
                        <span className="font-semibold capitalize">{job.trigger}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium border flex items-center gap-1 w-fit ${job.status === 'done' ? 'bg-green-100 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800' :
                          job.status === 'running' ? 'bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-900/30 dark:text-amber-400 dark:border-amber-800 animate-pulse' :
                            'bg-red-100 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800'
                        }`}>
                        {job.status === 'done' && <CheckCircle2 className="w-3 h-3" />}
                        {job.status === 'failed' && <AlertTriangle className="w-3 h-3" />}
                        {job.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1.5 font-mono text-zinc-600 dark:text-zinc-400">
                        <FileText className="w-4 h-4" /> {job.chunks_stored}
                      </div>
                    </td>
                    <td className="px-6 py-4 max-w-[250px]">
                      {job.error ? (
                        <div className="text-red-600 dark:text-red-400 text-xs bg-red-50 dark:bg-red-900/10 p-2 rounded-lg border border-red-100 dark:border-red-900/30 truncate hover:whitespace-normal hover:wrap-break-word cursor-help" title={job.error}>
                          {job.error}
                        </div>
                      ) : (
                        <span className="text-zinc-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-zinc-500">
                      {new Date(job.started_at).toLocaleString('id-ID', { dateStyle: 'short', timeStyle: 'short' })}
                    </td>
                    <td className="px-6 py-4 text-zinc-500">
                      {job.finished_at ? new Date(job.finished_at).toLocaleString('id-ID', { dateStyle: 'short', timeStyle: 'short' }) : 'Masih berjalan...'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default JobsPage;
