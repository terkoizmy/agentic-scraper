import { useEffect, useState } from 'react';
import axios from 'axios';
import { Database, Zap, FileText } from 'lucide-react';
import type { SourceDto, JobDto } from '../../types/dtos';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const DashboardPage = () => {
  const [sources, setSources] = useState<SourceDto[]>([]);
  const [jobs, setJobs] = useState<JobDto[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sourcesRes, jobsRes] = await Promise.all([
          axios.get<SourceDto[]>(`${API_BASE_URL}/sources`),
          axios.get<JobDto[]>(`${API_BASE_URL}/scrape/jobs`),
        ]);
        setSources(sourcesRes.data);
        setJobs(jobsRes.data);
      } catch (error) {
        console.error('Failed to fetch dashboard data', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  const totalDocuments = jobs.reduce((acc, job) => acc + (job.chunks_stored || 0), 0);
  const activeJobs = jobs.filter((job) => job.status === 'running').length;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-linear-to-r from-blue-600 to-indigo-500 mb-2">
        Dashboard Analytics
      </h1>
      <p className="text-zinc-500 mb-10 text-lg">
        Pemantauan metrik Agentic Scraper dan sumber data Anda secara real-time.
      </p>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 bg-zinc-200 dark:bg-zinc-800 rounded-xl" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
            <div className="flex items-center gap-3 text-zinc-500 dark:text-zinc-400 font-semibold mb-4">
              <Database className="w-5 h-5 text-blue-500" /> Web Sources
            </div>
            <p className="text-4xl font-bold text-zinc-900 dark:text-zinc-100">{sources.length}</p>
          </div>
          
          <div className="p-6 rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-sm hover:shadow-md transition-all flex flex-col justify-between relative overflow-hidden">
            {activeJobs > 0 && (
              <div className="absolute top-0 right-0 w-2 h-full bg-green-500 animate-pulse" />
            )}
            <div className="flex items-center gap-3 text-zinc-500 dark:text-zinc-400 font-semibold mb-4">
              <Zap className="w-5 h-5 text-amber-500" /> Active Jobs
            </div>
            <p className="text-4xl font-bold text-zinc-900 dark:text-zinc-100">{activeJobs}</p>
          </div>
          
          <div className="p-6 rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
            <div className="flex items-center gap-3 text-zinc-500 dark:text-zinc-400 font-semibold mb-4">
              <FileText className="w-5 h-5 text-indigo-500" /> Total Chunks Stored
            </div>
            <p className="text-4xl font-bold text-zinc-900 dark:text-zinc-100">{totalDocuments}</p>
          </div>
        </div>
      )}

      <div className="mt-12 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-6 shadow-sm">
        <h2 className="text-xl font-bold mb-6 text-zinc-900 dark:text-zinc-100">Scraping Jobs Terakhir</h2>
        {isLoading ? (
          <div className="h-40 flex items-center justify-center text-zinc-400">Memuat data...</div>
        ) : jobs.length === 0 ? (
          <div className="h-40 flex items-center justify-center text-zinc-400 bg-zinc-50 dark:bg-zinc-950/50 rounded-lg border border-dashed border-zinc-300 dark:border-zinc-700">Belum ada job / aktivitas scraping</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-zinc-500 uppercase bg-zinc-50 dark:bg-zinc-950/50 border-b border-zinc-200 dark:border-zinc-800">
                <tr>
                  <th className="px-6 py-3 font-semibold">Tipe Trigger</th>
                  <th className="px-6 py-3 font-semibold">Status</th>
                  <th className="px-6 py-3 font-semibold">Chunks Tersimpan</th>
                  <th className="px-6 py-3 font-semibold">Waktu Mulai</th>
                </tr>
              </thead>
              <tbody>
                {jobs.slice(0, 5).map((job) => (
                  <tr key={job.id} className="border-b border-zinc-100 dark:border-zinc-800/50 hover:bg-zinc-50 dark:hover:bg-zinc-800/20 transition-colors">
                    <td className="px-6 py-4 font-medium capitalize">{job.trigger}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${
                        job.status === 'done' ? 'bg-green-100 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800' :
                        job.status === 'running' ? 'bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-900/30 dark:text-amber-400 dark:border-amber-800' :
                        'bg-red-100 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800'
                      }`}>
                        {job.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-mono text-zinc-600 dark:text-zinc-400">{job.chunks_stored}</td>
                    <td className="px-6 py-4 text-zinc-500">
                      {new Date(job.started_at).toLocaleString('id-ID', { dateStyle: 'medium', timeStyle: 'short' })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
