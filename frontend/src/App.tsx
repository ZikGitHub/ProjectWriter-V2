import { useState, useEffect } from 'react'
import { getProjectState, initializeProject, generatePlan, executeTasks } from './api'
import './App.css'

function App() {
  const [state, setState] = useState<any>(null)
  const [request, setRequest] = useState('')
  const [loading, setLoading] = useState(false)

  const fetchState = async () => {
    try {
      const data = await getProjectState()
      setState(data)
    } catch (error) {
      console.error("Failed to fetch state", error)
    }
  }

  useEffect(() => {
    fetchState()
    const interval = setInterval(fetchState, 3000)
    return () => clearInterval(interval)
  }, [])

  const handleInitialize = async () => {
    setLoading(true)
    await initializeProject("Demo Project")
    await fetchState()
    setLoading(false)
  }

  const handlePlan = async () => {
    setLoading(true)
    await generatePlan(request)
    await fetchState()
    setLoading(false)
  }

  const handleExecute = async () => {
    await executeTasks()
  }

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white font-mono">
      <header className="p-4 border-b border-gray-700 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold">ProjectWriter-V2</h1>
          <button 
            onClick={handleInitialize}
            className="text-xs bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded"
          >
            Init Project
          </button>
        </div>
        <div className="flex gap-4">
          <span className="bg-green-600 px-2 py-1 rounded text-xs">
            Status: {state?.tasks?.some((t: any) => t.status === 'in_progress') ? 'Executing' : 'Idle'}
          </span>
          <span className="bg-blue-600 px-2 py-1 rounded text-xs">SLM: Qwen2.5-Coder</span>
        </div>
      </header>
      
      <main className="flex flex-1 overflow-hidden">
        <aside className="w-64 border-r border-gray-700 p-4 overflow-y-auto">
          <h2 className="text-sm font-semibold mb-4 text-gray-400">TASKS</h2>
          <div className="space-y-2">
            {state?.tasks?.map((task: any) => (
              <div key={task.id} className="text-xs p-2 bg-gray-800 rounded border border-gray-700">
                <div className="flex justify-between mb-1">
                  <span className="font-bold">{task.id}</span>
                  <span className={`px-1 rounded ${
                    task.status === 'completed' ? 'bg-green-900 text-green-300' : 
                    task.status === 'in_progress' ? 'bg-yellow-900 text-yellow-300' : 'bg-gray-700'
                  }`}>
                    {task.status}
                  </span>
                </div>
                <div className="text-gray-400 truncate">{task.description}</div>
              </div>
            ))}
          </div>
        </aside>
        
        <section className="flex-1 flex flex-col">
          <div className="p-4 border-b border-gray-700 flex gap-2">
            <input 
              type="text" 
              value={request}
              onChange={(e) => setRequest(e.target.value)}
              placeholder="Enter feature request..."
              className="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-1 text-sm focus:outline-none focus:border-blue-500"
            />
            <button 
              onClick={handlePlan}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-500 px-4 py-1 rounded text-sm disabled:opacity-50"
            >
              Plan
            </button>
            <button 
              onClick={handleExecute}
              className="bg-green-600 hover:bg-green-500 px-4 py-1 rounded text-sm"
            >
              Run
            </button>
          </div>
          
          <div className="flex-1 bg-gray-950 p-4 overflow-auto">
            <h2 className="text-sm font-semibold mb-4 text-gray-400">ACTIVE LOGS</h2>
            <div className="text-xs space-y-1">
              {state?.tasks?.filter((t: any) => t.error).map((t: any) => (
                <div key={t.id} className="text-red-400">
                  [{t.id}] Error: {t.error}
                </div>
              ))}
              {state?.tasks?.filter((t: any) => t.status === 'completed').map((t: any) => (
                <div key={t.id} className="text-green-400">
                  [{t.id}] Task completed: {t.file_path}
                </div>
              ))}
            </div>
          </div>
          
          <footer className="h-48 border-t border-gray-700 bg-black p-4 overflow-y-auto">
            <h2 className="text-sm font-semibold mb-2 text-gray-400">ENGINE TERMINAL</h2>
            <div className="text-xs text-gray-300">
              Welcome to ProjectWriter-V2.<br/>
              Project: {state?.project_name || 'None'}<br/>
              Ready for input.
            </div>
          </footer>
        </section>
      </main>
    </div>
  )
}

export default App
