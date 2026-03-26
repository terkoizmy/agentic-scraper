import { BrowserRouter, Routes, Route, Link } from "react-router-dom"
import { Bot, Database, Blocks } from "lucide-react"

// Temporary stub pages until we create the real ones in src/pages
const Dashboard = () => (
  <div className="p-8">
    <h1 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-500">
      Agentic Scraper
    </h1>
    <p className="mt-4 text-muted-foreground text-lg">
      Welcome to the MiniMax LLM-orchestrated web scraper.
    </p>

    <div className="grid grid-cols-3 gap-6 mt-10">
      <div className="p-6 rounded-xl border bg-card/60 backdrop-blur-sm shadow-sm transition-all hover:shadow-md">
        <h3 className="font-semibold text-xl">Sources</h3>
        <p className="text-3xl font-bold mt-2">0</p>
      </div>
      <div className="p-6 rounded-xl border bg-card/60 backdrop-blur-sm shadow-sm transition-all hover:shadow-md">
        <h3 className="font-semibold text-xl">Running Jobs</h3>
        <p className="text-3xl font-bold mt-2">0</p>
      </div>
      <div className="p-6 rounded-xl border bg-card/60 backdrop-blur-sm shadow-sm transition-all hover:shadow-md">
        <h3 className="font-semibold text-xl">Documents</h3>
        <p className="text-3xl font-bold mt-2">0</p>
      </div>
    </div>
  </div>
)

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
            <Route path="/" element={<Dashboard />} />
            <Route path="/agent" element={<div className="p-8"><h2 className="text-2xl font-bold">Agent Chat / Console</h2></div>} />
            <Route path="/sources" element={<div className="p-8"><h2 className="text-2xl font-bold">Manage Sources</h2></div>} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
