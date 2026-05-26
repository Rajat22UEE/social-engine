'use client';
import { useState, useEffect } from 'react';

export default function Home() {
  const [view, setView] = useState('create'); // Default to create
  const [topic, setTopic] = useState('');
  const [templates, setTemplates] = useState<{id: number, name: string}[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<number>(1);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{content: string, image_path: string} | null>(null);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/templates')
      .then(res => res.json())
      .then(data => setTemplates(data))
      .catch(err => console.error("Error fetching templates:", err));
  }, []);

  const handleCreate = async () => {
    if (!topic) return alert("Please enter a topic!");
    setLoading(true);
    setResult(null);
    
    try {
      const res = await fetch('http://127.0.0.1:8000/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, template_id: selectedTemplate }),
      });
      
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setResult(data);
    } catch (err: any) {
      alert("Error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#0f172a] text-white">
      {/* Sidebar */}
      <aside className="w-72 bg-white/5 backdrop-blur-xl border-r border-white/10 p-6 flex flex-col">
        <h1 className="text-2xl font-bold tracking-tight mb-10">AI Workspace</h1>
        <nav className="space-y-3">
          <button onClick={() => setView('dashboard')} className={`w-full text-left px-4 py-3 rounded-xl transition ${view === 'dashboard' ? 'bg-blue-600' : 'bg-white/5 hover:bg-white/10'}`}>Dashboard</button>
          <button onClick={() => setView('create')} className={`w-full text-left px-4 py-3 rounded-xl transition ${view === 'create' ? 'bg-blue-600' : 'bg-white/5 hover:bg-white/10'}`}>Create Post</button>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-auto">
        {view === 'create' ? (
          <div className="max-w-2xl bg-white/5 border border-white/10 rounded-3xl p-8 space-y-6">
            <h1 className="text-3xl font-bold">Create New Post</h1>
            
            <div className="space-y-2">
              <label className="text-sm text-gray-400">Select Template</label>
              <select 
                className="w-full bg-[#1e293b] p-3 rounded-xl border border-white/10 focus:ring-2 focus:ring-blue-500 outline-none"
                onChange={(e) => setSelectedTemplate(Number(e.target.value))}
              >
                {templates.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
              </select>
            </div>

            <input 
              value={topic} 
              onChange={(e) => setTopic(e.target.value)} 
              placeholder="Enter content topic..." 
              className="w-full bg-[#1e293b] p-3 rounded-xl border border-white/10 focus:ring-2 focus:ring-blue-500 outline-none" 
            />
            
            <button 
              onClick={handleCreate} 
              disabled={loading} 
              className="w-full bg-blue-600 hover:bg-blue-500 py-3 rounded-xl font-bold transition"
            >
              {loading ? "Generating Assets..." : "Generate Content & Image"}
            </button>

            {result && (
              <div className="border-t border-white/10 pt-6 space-y-4 animate-in fade-in duration-500">
                <h3 className="font-semibold text-gray-200">Generated Content:</h3>
                <p className="text-gray-300 whitespace-pre-line bg-[#1e293b] p-4 rounded-xl">{result.content}</p>
                <a 
                  href={`http://127.0.0.1:8000/${result.image_path}`} 
                  target="_blank"
                  className="block w-full text-center bg-green-600 hover:bg-green-500 py-3 rounded-xl font-bold transition"
                >
                  Download Generated Image
                </a>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center mt-20 text-gray-500">Dashboard stats coming soon...</div>
        )}
      </main>
    </div>
  );
}