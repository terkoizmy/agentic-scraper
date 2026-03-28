import { BrowserRouter, Routes, Route, Link } from "react-router-dom"
import { Bot, Database, Blocks } from "lucide-react"
import AgentPage from "./pages/agent/agent-page"

import DashboardPage from "./pages/dashboard/dashboard-page"
import SourcesPage from "./pages/sources/sources-page"

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen w-full bg-background dark:bg-zinc-950 font-sans">
        
        {/* Sidebar */}
        <aside className="w-64 border-r border-border/50 bg-zinc-50/50 dark:bg-zinc-900/50 px-4 py-8 flex flex-col gap-4">
          <div className="font-black flex items-center gap-2 px-2 text-xl mb-6 text-zinc-800 dark:text-zinc-100">
            <Bot className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            AgenticScrape
          </div>
          <nav className="flex flex-col gap-1.5 flex-1">
            <Link to="/" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-zinc-200 dark:hover:bg-zinc-800 transition-colors font-medium">
              <Blocks className="w-4 h-4 text-zinc-500" /> Dashboard
            </Link>
            <Link to="/agent" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-zinc-200 dark:hover:bg-zinc-800 transition-colors font-medium">
              <Bot className="w-4 h-4 text-zinc-500" /> Agent Console
            </Link>
            <Link to="/sources" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-zinc-200 dark:hover:bg-zinc-800 transition-colors font-medium">
              <Database className="w-4 h-4 text-zinc-500" /> Web Sources
            </Link>
          </nav>
        </aside>

        {/* Content Area */}
        <main className="flex-1 overflow-auto bg-white dark:bg-zinc-950">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/agent" element={<AgentPage />} />
            <Route path="/sources" element={<SourcesPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
