"use client";
import { useState } from "react";
import { useSession } from "../hooks/useSession";
import Dashboard from "./components/Dashboard";
import CreateWizard from "./components/CreateWizard";

export default function Home() {
  const { session, loading: sessionLoading } = useSession();
  const [view, setView] = useState("create");

  return (
    <div className="flex h-screen bg-[#0f172a] text-white">
      {/* Sidebar */}
      <aside className="w-72 bg-white/5 backdrop-blur-xl border-r border-white/10 p-6 flex flex-col">
        <h1 className="text-2xl font-bold tracking-tight mb-2">AI Workspace</h1>
        
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
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-auto">
        {view === "create" ? (
          <div className="max-w-3xl mx-auto space-y-6">
            <CreateWizard />
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