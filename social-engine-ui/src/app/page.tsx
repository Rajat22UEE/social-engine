"use client";
import { useState, useEffect } from "react";
import { useSession } from "../hooks/useSession";
import { useBrandKit } from "../hooks/useBrandKit";
import BrandKitManager from "./components/BrandKitManager";
import ExportButtons from "./components/ExportButtons";
import Dashboard from "./components/Dashboard";
import CanvasEditor from "./components/CanvasEditor";
import CreateWizard from "./components/CreateWizard";

export default function Home() {
  const { session, loading: sessionLoading } = useSession();
  const { brandKit, loading: brandKitLoading } = useBrandKit();
  const [view, setView] = useState("create"); // Default to create
  const [topic, setTopic] = useState("");
  const [templates, setTemplates] = useState<{ id: number; name: string }[]>(
    [],
  );
  const [selectedTemplate, setSelectedTemplate] = useState<number>(1);
  const [loading, setLoading] = useState(false);
  const [showCanvasEditor, setShowCanvasEditor] = useState(false);
  const [result, setResult] = useState<{
    post_id: number;
    headline: string;
    hook: string;
    caption: string;
    cta: string;
    hashtags: string[];
    image_path: string;
  } | null>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/templates")
      .then((res) => res.json())
      .then((data) => setTemplates(data))
      .catch((err) => console.error("Error fetching templates:", err));
  }, []);

  const handleCreate = async () => {
    if (!topic) return alert("Please enter a topic!");
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, template_id: selectedTemplate }),
      });

      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setResult({
        post_id: data.post_id,
        headline: data.headline,
        hook: data.hook,
        caption: data.caption,
        cta: data.cta,
        hashtags: data.hashtags,
        image_path: data.image_path,
      });
      setShowCanvasEditor(false);
    } catch (err) {
      alert("Error: " + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    alert(`${label} copied to clipboard!`);
  };

  const copyPostDescription = () => {
    if (!result) return;
    const postText = [result.caption, result.cta, result.hashtags.join(" ")].filter(Boolean).join("\n\n");
    navigator.clipboard.writeText(postText);
    alert("Post description copied to clipboard!");
  };

  return (
    <div className="flex h-screen bg-[#0f172a] text-white">
      {/* Sidebar */}
      <aside className="w-72 bg-white/5 backdrop-blur-xl border-r border-white/10 p-6 flex flex-col">
        <h1 className="text-2xl font-bold tracking-tight mb-2">
          AI Workspace
        </h1>
        
        {/* Session Indicator */}
        <div className="mb-6 p-3 bg-white/5 rounded-xl border border-white/10">
          <p className="text-xs text-gray-400 mb-1">Session</p>
          {sessionLoading ? (
            <p className="text-xs text-gray-500">Loading...</p>
          ) : session ? (
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <p className="text-xs text-green-400 truncate" title={session.session_id}>
                {session.session_id.slice(0, 8)}...
              </p>
            </div>
          ) : (
            <p className="text-xs text-red-400">Not connected</p>
          )}
        </div>

        <nav className="space-y-3">
          <button
            onClick={() => setView("dashboard")}
            className={`w-full text-left px-4 py-3 rounded-xl transition ${view === "dashboard" ? "bg-blue-600" : "bg-white/5 hover:bg-white/10"}`}
          >
            Dashboard
          </button>
          <button
            onClick={() => setView("create")}
            className={`w-full text-left px-4 py-3 rounded-xl transition ${view === "create" ? "bg-blue-600" : "bg-white/5 hover:bg-white/10"}`}
          >
            Create Post
          </button>
          <button
            onClick={() => setView("brandkit")}
            className={`w-full text-left px-4 py-3 rounded-xl transition ${view === "brandkit" ? "bg-blue-600" : "bg-white/5 hover:bg-white/10"}`}
          >
            Brand Kit
          </button>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-auto">
        {view === "create" ? (
          <div className="max-w-3xl mx-auto space-y-6">
            <CreateWizard />
          </div>
        ) : view === "brandkit" ? (
          <div className="max-w-2xl mx-auto">
            <BrandKitManager />
          </div>
        ) : (
          <div className="max-w-5xl mx-auto">
            <Dashboard />
          </div>
        )}
      </main>
    </div>
  );
}